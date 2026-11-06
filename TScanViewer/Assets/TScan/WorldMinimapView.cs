using System;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

namespace Steve.TScan {
 // Read-only projection of the same confirmed snapshot the agent receives. No builder/agent commands.
 public sealed class WorldMinimapView {
  public VisualElement Root {get;}
  readonly VisualElement map;readonly Label title,summary,notice;GridSnapshot snapshot;string observation="";
  public WorldMinimapView(VisualElement parent){
   Root=new VisualElement{name="watch-world-minimap"};Root.AddToClassList("watch-world-minimap");parent.Add(Root);
   var frame=new VisualElement{pickingMode=PickingMode.Ignore};frame.AddToClassList("watch-map-frame");Root.Add(frame);
   title=Label("WORLD STATE · N ↑","watch-map-title");map=new VisualElement{name="watch-map-cells"};map.AddToClassList("watch-map-cells");Root.Add(map);map.generateVisualContent+=Paint;
   Label("Mint: Steve · Red: target","watch-map-legend").AddToClassList("map-legend-first");Label("Gray: blocked · Orange: hazard","watch-map-legend").AddToClassList("map-legend-second");
   summary=Label("Waiting for world","watch-map-summary");notice=Label("","watch-map-notice");
   Root.tooltip="Confirmed world state. North is up; coordinates are x/y from 1. This map does not issue movement or edit the world.";
  }
  Label Label(string text,string css){var l=new Label(text);l.AddToClassList(css);Root.Add(l);return l;}
  public void Update(GridSnapshot current,bool fresh,bool draftPending){
   if(fresh&&current!=null)snapshot=current;
   Root.EnableInClassList("stale",!fresh);
   var next=(snapshot?.observation_id??"")+"|"+fresh;
   if(next!=observation){observation=next;map.MarkDirtyRepaint();}
   int alive=snapshot?.training_targets?.Count(t=>t.hp>0)??0;
   title.text=(fresh?"WORLD STATE":"STALE WORLD")+" · N ↑";
   summary.text=snapshot==null?"Waiting for world":(snapshot.board?.columns??15)+" × "+(snapshot.board?.rows??15)+" · "+alive+" targets · tick "+snapshot.game_tick;
   notice.text=draftPending?"Unapplied world draft · Build to apply":!fresh?"Waiting for fresh world feedback":"";
   notice.style.display=string.IsNullOrEmpty(notice.text)?DisplayStyle.None:DisplayStyle.Flex;
   Root.style.height=string.IsNullOrEmpty(notice.text)?284:324;
  }
  static Color Flag(string color)=>color=="red"?new Color(1,.27f,.29f):color=="blue"?new Color(.25f,.57f,1):color=="yellow"?new Color(1,.84f,.22f):color=="purple"?new Color(.73f,.40f,1):new Color(1,.57f,.24f);
  void Paint(MeshGenerationContext context){
   if(snapshot?.board==null)return;
   int columns=snapshot.board.columns,rows=snapshot.board.rows;if(columns<1||rows<1)return;
   var painter=context.painter2D;float cell=Mathf.Min(map.contentRect.width/columns,map.contentRect.height/rows),ox=(map.contentRect.width-cell*columns)/2,oy=(map.contentRect.height-cell*rows)/2;
   void Box(float x,float y,float width,float height,Color color){painter.fillColor=color;painter.BeginPath();painter.MoveTo(new Vector2(x,y));painter.LineTo(new Vector2(x+width,y));painter.LineTo(new Vector2(x+width,y+height));painter.LineTo(new Vector2(x,y+height));painter.ClosePath();painter.Fill();}
   void Cell(int x,int y,Color color,float inset=1){if(x<1||x>columns||y<1||y>rows)return;Box(ox+(x-1)*cell+inset,oy+(rows-y)*cell+inset,Mathf.Max(1,cell-2*inset),Mathf.Max(1,cell-2*inset),color);}
   for(int y=1;y<=rows;y++)for(int x=1;x<=columns;x++)Cell(x,y,new Color(.11f,.17f,.20f),.5f);
   foreach(var item in snapshot.visible_obstacles??Array.Empty<GridFeature>())Cell(item.col,item.row,new Color(.43f,.49f,.53f));
   foreach(var item in snapshot.visible_hazards??Array.Empty<GridFeature>())Cell(item.col,item.row,new Color(1,.53f,.16f));
   foreach(var item in snapshot.visible_targets??Array.Empty<GridLandmark>())Cell(item.col,item.row,Flag(item.color),2);
   foreach(var item in snapshot.training_targets??Array.Empty<TrainingTarget>())Cell(item.col,item.row,item.hp>0?new Color(1,.31f,.35f):new Color(.37f,.20f,.24f),2);
   if(snapshot.self!=null)Cell(snapshot.self.col,snapshot.self.row,new Color(.28f,1,.82f),1);
  }
 }
}
