using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Steve.TScan {
 // The user's draft of the 15 x 15 world. It owns every placement rule, mirroring the backend's role rules
 // (world_manifest.py) so an invalid world cannot be built here. The backend still re-validates on publish.
 public sealed class WorldBuilder {
  public const int Size=15;
  public string[] Floors=new string[Size*Size];
  public readonly List<MeadowPlacement> Obstacles=new List<MeadowPlacement>();   // blocking pieces
  public readonly List<MeadowPlacement> Props=new List<MeadowPlacement>();       // walkable pieces
  public readonly List<GridLandmark> Landmarks=new List<GridLandmark>();
  public MeadowCell Spawn=new MeadowCell();
  public bool Dirty {get;private set;}
  public void MarkClean(){Dirty=false;}
  public static readonly string[] FlagColors={"blue","red","yellow","purple","orange"};

  public WorldBuilder(MeadowManifest source){Load(source);Dirty=false;}

  public static string DefaultFloor(){
   WorldKit.EnsureLoaded();
   var preferred=WorldKit.Info("dungeon_floor_flag_a");
   return preferred!=null?preferred.id:WorldKit.Pieces.Where(p=>p.role==WorldKit.FloorRole).OrderBy(p=>p.id).Select(p=>p.id).FirstOrDefault();
  }

  public void Load(MeadowManifest m){
   var floor=DefaultFloor();Floors=new string[Size*Size];
   for(int i=0;i<Floors.Length;i++)Floors[i]=m.floors!=null&&i<m.floors.Length&&WorldKit.Info(m.floors[i])?.role==WorldKit.FloorRole?m.floors[i]:floor;
   Obstacles.Clear();foreach(var o in m.obstacles??Array.Empty<MeadowPlacement>())if(WorldKit.Info(o.prototype)!=null)Obstacles.Add(Copy(o));
   Props.Clear();foreach(var p in m.props??Array.Empty<MeadowPlacement>())if(WorldKit.Info(p.prototype)!=null)Props.Add(Copy(p));
   Landmarks.Clear();foreach(var l in m.landmarks??Array.Empty<GridLandmark>())Landmarks.Add(new GridLandmark{id=l.id,name=l.name,color=l.color,kind=l.kind,col=l.col,row=l.row,occupiable=l.occupiable});
   Spawn=new MeadowCell{col=m.spawn?.col??8,row=m.spawn?.row??8};Dirty=true;
  }
  static MeadowPlacement Copy(MeadowPlacement p)=>new MeadowPlacement{id=p.id,prototype=p.prototype,col=p.col,row=p.row,yaw=p.yaw};

  public MeadowManifest ToManifest(int revision){
   var used=new HashSet<string>(Floors);foreach(var o in Obstacles)used.Add(o.prototype);foreach(var p in Props)used.Add(p.prototype);
   var catalog=used.Select(id=>WorldKit.Info(id)).Where(info=>info!=null).OrderBy(info=>info.id,StringComparer.Ordinal).Select(info=>new MeadowCatalogEntry{prototype=info.id,name=info.name,role=info.role,blocks=info.blocks,footprint=WorldKit.FootprintOf(info)}).ToArray();
   return new MeadowManifest{schema=MeadowEnvironment.KitSchema,world_id="steve_grid_v1",revision=revision,columns=Size,rows=Size,
    landmarks=Landmarks.OrderBy(l=>l.id,StringComparer.Ordinal).ToArray(),spawn=new MeadowCell{col=Spawn.col,row=Spawn.row},
    obstacles=Obstacles.OrderBy(o=>o.id,StringComparer.Ordinal).Select(Copy).ToArray(),floors=(string[])Floors.Clone(),
    props=Props.OrderBy(p=>p.id,StringComparer.Ordinal).Select(Copy).ToArray(),catalog=catalog};
  }

  public static bool InBoard(int col,int row)=>col>=1&&col<=Size&&row>=1&&row<=Size;
  static int Index(int col,int row)=>(row-1)*Size+(col-1);
  public bool IsSpawn(int col,int row)=>Spawn.col==col&&Spawn.row==row;
  // A blocker covers its anchor cell, or the cells around it when its piece has a larger footprint (3 x 3 for big actors).
  static int Half(MeadowPlacement o)=>WorldKit.FootprintOf(WorldKit.Info(o.prototype))/2;
  static bool Covers(MeadowPlacement o,int col,int row){int h=Half(o);return Math.Abs(o.col-col)<=h&&Math.Abs(o.row-row)<=h;}
  public MeadowPlacement BlockerAt(int col,int row)=>Obstacles.FirstOrDefault(o=>Covers(o,col,row));
  public MeadowPlacement PropAt(int col,int row)=>Props.FirstOrDefault(p=>p.col==col&&p.row==row);
  public GridLandmark FlagAt(int col,int row)=>Landmarks.FirstOrDefault(l=>l.col==col&&l.row==row);
  public string FloorAt(int col,int row)=>Floors[Index(col,row)];

  // ----- placement. commit=false asks "would this work?" without changing anything.
  public bool TryPlace(KitPieceInfo piece,int col,int row,int yaw,bool commit,out string why){
   why=null;
   if(piece==null){why="Pick a piece first.";return false;}
   if(!InBoard(col,row)){why="That cell is outside the 15 x 15 world.";return false;}
   if(piece.role==WorldKit.FloorRole){if(commit&&Floors[Index(col,row)]!=piece.id){Floors[Index(col,row)]=piece.id;Dirty=true;}return true;}
   if(piece.blocks){
    int half=WorldKit.FootprintOf(piece)/2;
    if(!InBoard(col-half,row-half)||!InBoard(col+half,row+half)){why="That "+piece.name.ToLowerInvariant()+" would hang off the edge of the world.";return false;}
    for(int c=col-half;c<=col+half;c++)for(int r=row-half;r<=row+half;r++){
     if(IsSpawn(c,r)){why="The spawn cell has to stay open.";return false;}
     if(FlagAt(c,r)!=null){why="A flag is on one of those cells. Move the flag first.";return false;}
     var other=Obstacles.FirstOrDefault(o=>Covers(o,c,r)&&!(o.col==col&&o.row==row&&half==0));
     if(other!=null&&(half>0||Half(other)>0)){why="Erase the "+WorldKit.Info(other.prototype).name.ToLowerInvariant()+" first; it is in the way.";return false;}
    }
    if(commit){
     for(int c=col-half;c<=col+half;c++)for(int r=row-half;r<=row+half;r++){int cc=c,rr=r;Props.RemoveAll(p=>p.col==cc&&p.row==rr);Obstacles.RemoveAll(o=>o.col==cc&&o.row==rr);}
     Obstacles.Add(new MeadowPlacement{id="o_"+col+"_"+row,prototype=piece.id,col=col,row=row,yaw=yaw});Dirty=true;
    }
    return true;
   }
   if(BlockerAt(col,row)!=null){why="Erase the "+WorldKit.Info(BlockerAt(col,row).prototype).name.ToLowerInvariant()+" first; it blocks that cell.";return false;}
   if(piece.role==WorldKit.HazardRole&&(IsSpawn(col,row)||FlagAt(col,row)!=null)){why="A hazard cannot sit on the spawn or a flag.";return false;}
   if(commit){Props.RemoveAll(p=>p.col==col&&p.row==row);Props.Add(new MeadowPlacement{id="p_"+col+"_"+row,prototype=piece.id,col=col,row=row,yaw=yaw});Dirty=true;}
   return true;
  }

  public bool TrySpawn(int col,int row,bool commit,out string why){
   why=null;
   if(!InBoard(col,row)){why="That cell is outside the 15 x 15 world.";return false;}
   if(BlockerAt(col,row)!=null){why="The spawn cell cannot be blocked.";return false;}
   var prop=PropAt(col,row);if(prop!=null&&WorldKit.Info(prop.prototype)?.role==WorldKit.HazardRole){why="The spawn cell cannot be a hazard.";return false;}
   if(commit&&!IsSpawn(col,row)){Spawn=new MeadowCell{col=col,row=row};Dirty=true;}
   return true;
  }

  public bool TryFlag(string color,int col,int row,bool commit,out string why){
   why=null;
   if(!InBoard(col,row)){why="That cell is outside the 15 x 15 world.";return false;}
   if(BlockerAt(col,row)!=null){why="A flag cannot go on a blocked cell.";return false;}
   if(IsSpawn(col,row)){why="A flag cannot sit on the spawn.";return false;}
   var prop=PropAt(col,row);if(prop!=null&&WorldKit.Info(prop.prototype)?.role==WorldKit.HazardRole){why="A flag cannot sit on a hazard.";return false;}
   if(commit){
    Landmarks.RemoveAll(l=>l.col==col&&l.row==row||l.color==color);
    Landmarks.Add(new GridLandmark{id="target_"+color,name=char.ToUpperInvariant(color[0])+color.Substring(1)+" flag",color=color,kind="flag",col=col,row=row,occupiable=true});Dirty=true;
   }
   return true;
  }

  // Erase removes the top item: a walkable prop first, then a blocker, then a flag. Floors are replaced, never erased.
  public bool TryErase(int col,int row,bool commit,out string why){
   why=null;
   if(!InBoard(col,row)){why="That cell is outside the 15 x 15 world.";return false;}
   bool any=PropAt(col,row)!=null||BlockerAt(col,row)!=null||FlagAt(col,row)!=null;
   if(!any){why="Nothing to erase there. Floors are replaced, not erased.";return false;}
   if(commit){
    if(Props.RemoveAll(p=>p.col==col&&p.row==row)==0&&Obstacles.RemoveAll(o=>Covers(o,col,row))==0)Landmarks.RemoveAll(l=>l.col==col&&l.row==row);
    Dirty=true;
   }
   return true;
  }

  // ----- the same playability rule the backend enforces: every flag reachable from the spawn.
  public string Unreachable(){
   var blocked=new HashSet<int>();foreach(var o in Obstacles){int h=Half(o);for(int c=o.col-h;c<=o.col+h;c++)for(int r=o.row-h;r<=o.row+h;r++)if(InBoard(c,r))blocked.Add(Index(c,r));}
   var seen=new HashSet<int>{Index(Spawn.col,Spawn.row)};var queue=new Queue<int>(seen);
   int[] dc={1,-1,0,0},dr={0,0,1,-1};
   while(queue.Count>0){
    int at=queue.Dequeue(),c=at%Size+1,r=at/Size+1;
    for(int k=0;k<4;k++){int nc=c+dc[k],nr=r+dr[k];if(!InBoard(nc,nr))continue;int next=Index(nc,nr);if(blocked.Contains(next)||seen.Contains(next))continue;seen.Add(next);queue.Enqueue(next);}
   }
   var lost=Landmarks.Where(l=>!seen.Contains(Index(l.col,l.row))).Select(l=>l.name).ToArray();
   return lost.Length==0?null:string.Join(", ",lost)+(lost.Length==1?" cannot":" cannot")+" be reached from the spawn.";
  }

  // ----- saved worlds: plain manifest JSON the backend would accept as published.
  public static string Folder=>Path.Combine(Application.persistentDataPath,"Worlds");
  static string Clean(string name){var kept=new string((name??"").Trim().Select(c=>char.IsLetterOrDigit(c)||c=='-'||c=='_'?c:'-').ToArray());return kept.Length==0?"world":kept.Substring(0,Mathf.Min(40,kept.Length));}
  public static string[] SavedNames(){try{if(!Directory.Exists(Folder))return Array.Empty<string>();return Directory.GetFiles(Folder,"*.json").Select(Path.GetFileNameWithoutExtension).Where(n=>!n.StartsWith("_")).OrderBy(n=>n,StringComparer.OrdinalIgnoreCase).ToArray();}catch{return Array.Empty<string>();}}
  // The last applied world is remembered, because the backend refuses a lower revision than the one it confirmed.
  public static string CurrentPath=>Path.Combine(Folder,"_current.json");
  public static void SaveCurrent(MeadowManifest manifest){try{Directory.CreateDirectory(Folder);File.WriteAllText(CurrentPath,JsonUtility.ToJson(manifest,true));}catch(Exception e){Debug.LogWarning("Could not remember the applied world: "+e.Message);}}
  public static MeadowManifest LoadCurrent(int minimumRevision){
   try{if(!File.Exists(CurrentPath))return null;var loaded=new MeadowManifest();JsonUtility.FromJsonOverwrite(File.ReadAllText(CurrentPath),loaded);return loaded.schema==MeadowEnvironment.KitSchema&&loaded.revision>=minimumRevision?loaded:null;}
   catch{return null;}
  }
  public string Save(string name,int revision){Directory.CreateDirectory(Folder);var file=Clean(name);File.WriteAllText(Path.Combine(Folder,file+".json"),JsonUtility.ToJson(ToManifest(revision),true));return file;}
  public bool TryLoad(string name,out string why){
   why=null;var path=Path.Combine(Folder,Clean(name)+".json");
   try{var loaded=new MeadowManifest();JsonUtility.FromJsonOverwrite(File.ReadAllText(path),loaded);if(loaded.schema!=MeadowEnvironment.KitSchema){why="That file is not a built world.";return false;}Load(loaded);return true;}
   catch(Exception e){why="Could not load "+name+": "+e.Message;return false;}
  }
 }
}
