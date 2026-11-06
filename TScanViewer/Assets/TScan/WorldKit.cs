using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEngine.Rendering;

namespace Steve.TScan {
 [Serializable] public class KitPieceInfo {public string id,name,role,category,pack,note;public bool blocks;public int footprint=1;public string tier;public float height;public int vertices,triangles;}
 [Serializable] public class KitCatalogFile {public string pack,title;public KitPieceInfo[] pieces;}

 // Baked, vertex-coloured kit pieces and their role catalog (written by t-scan/art/export_kit.py).
 // A piece's role is fixed at export. Nothing in Unity re-labels it.
 public static class WorldKit {
  public const string FloorRole="floor",WallRole="wall",ObstacleRole="obstacle",StructureRole="structure",HazardRole="hazard",DecorRole="decor",ActorRole="actor";
  static bool loaded;
  static readonly Dictionary<string,KitPieceInfo> pieces=new Dictionary<string,KitPieceInfo>();
  static readonly Dictionary<string,Mesh> meshes=new Dictionary<string,Mesh>();
  static readonly List<string> packOrder=new List<string>();
  static readonly Dictionary<string,string> packTitles=new Dictionary<string,string>();
  public static IReadOnlyList<string> Packs {get{EnsureLoaded();return packOrder;}}
  public static string PackTitle(string pack)=>packTitles.TryGetValue(pack,out var title)?title:pack;
  public static IEnumerable<KitPieceInfo> Pieces {get{EnsureLoaded();return pieces.Values;}}
  public static KitPieceInfo Info(string id){EnsureLoaded();return id!=null&&pieces.TryGetValue(id,out var info)?info:null;}
  public static Mesh MeshOf(string id){EnsureLoaded();return id!=null&&meshes.TryGetValue(id,out var mesh)?mesh:null;}
  public static void Reload(){loaded=false;foreach(var mesh in meshes.Values)if(mesh){if(Application.isPlaying)UnityEngine.Object.Destroy(mesh);else UnityEngine.Object.DestroyImmediate(mesh);}meshes.Clear();pieces.Clear();packOrder.Clear();packTitles.Clear();EnsureLoaded();}

  public static void EnsureLoaded(){
   if(loaded)return;loaded=true;
   var assets=Resources.LoadAll<TextAsset>("Meadow/kit");
   foreach(var asset in assets)if(asset.name.StartsWith("catalog_")){
    var file=JsonUtility.FromJson<KitCatalogFile>(asset.text);if(file?.pieces==null)continue;
    if(!packOrder.Contains(file.pack)){packOrder.Add(file.pack);packTitles[file.pack]=file.title;}
    foreach(var info in file.pieces)pieces[info.id]=info;
   }
   foreach(var asset in assets)if(asset.name.StartsWith("kit_")){
    try{Parse(asset.bytes);}catch(Exception e){Debug.LogError("Kit "+asset.name+" could not be read: "+e.Message);}
   }
  }

  static void Parse(byte[] data){
   using(var reader=new BinaryReader(new MemoryStream(data))){
    var magic=reader.ReadBytes(4);if(magic.Length<4||magic[0]!='S'||magic[1]!='K'||magic[2]!='I'||magic[3]!='T')throw new InvalidDataException("Not a kit file");
    reader.ReadUInt32();uint count=reader.ReadUInt32();
    for(uint piece=0;piece<count;piece++){
     string key=Encoding.UTF8.GetString(reader.ReadBytes(reader.ReadUInt16()));
     int vertexCount=(int)reader.ReadUInt32(),indexCount=(int)reader.ReadUInt32();
     var raw=reader.ReadBytes(vertexCount*12);var floats=new float[vertexCount*3];Buffer.BlockCopy(raw,0,floats,0,raw.Length);
     var vertices=new Vector3[vertexCount];for(int i=0;i<vertexCount;i++)vertices[i]=new Vector3(floats[3*i],floats[3*i+1],floats[3*i+2]);
     var packedNormals=reader.ReadBytes(vertexCount*4);var normals=new Vector3[vertexCount];
     for(int i=0;i<vertexCount;i++)normals[i]=new Vector3((sbyte)packedNormals[4*i],(sbyte)packedNormals[4*i+1],(sbyte)packedNormals[4*i+2]).normalized;
     var packedColors=reader.ReadBytes(vertexCount*4);var colors=new Color32[vertexCount];
     for(int i=0;i<vertexCount;i++)colors[i]=new Color32(packedColors[4*i],packedColors[4*i+1],packedColors[4*i+2],packedColors[4*i+3]);
     var rawIndices=reader.ReadBytes(indexCount*4);var indices=new int[indexCount];Buffer.BlockCopy(rawIndices,0,indices,0,rawIndices.Length);
     var mesh=new Mesh{name=key,indexFormat=vertexCount>65535?IndexFormat.UInt32:IndexFormat.UInt16,hideFlags=HideFlags.DontSave};
     mesh.vertices=vertices;mesh.normals=normals;mesh.colors32=colors;mesh.triangles=indices;mesh.RecalculateBounds();
     meshes[key]=mesh;
    }
   }
  }

  public static bool Blocks(string id)=>Info(id)?.blocks==true;
  public static string RoleOf(string id)=>Info(id)?.role;
  public static bool IsPlaceable(KitPieceInfo piece)=>piece!=null;
  public static int FootprintOf(KitPieceInfo piece)=>piece==null?1:Mathf.Max(1,piece.footprint);
  // What the builder files a piece under: its role, except that bosses are listed apart from other enemies.
  public static string CategoryOf(KitPieceInfo piece)=>piece==null?"":piece.role==ActorRole&&piece.tier=="boss"?"boss":piece.role;
 }
}
