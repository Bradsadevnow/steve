using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
namespace Steve.TScan {
 public sealed partial class TScanViewer {
 [Serializable] public class MemoryGraphNode {public string id,label,detail,group,stage,source_path;public int source_line;public bool hub;}
 [Serializable] public class MemoryGraphEdge {public string source,target,relation;}
 [Serializable] public class MemoryGraph {public MemoryGraphNode[] nodes;public MemoryGraphEdge[] edges;public int record_count;}
 [Serializable] public class MemoryGraphs {public MemoryGraph conversation,development;}
 MemoryGraphs memoryGraphs;bool developmentGraph;string selectedMemory="",graphConnection="Connecting";Texture2D graphGlow;
 IEnumerator PollMemoryGraphs(){while(true){using(var req=UnityWebRequest.Get(Endpoint+"/memory_graphs")){req.timeout=4;yield return req.SendWebRequest();if(req.result==UnityWebRequest.Result.Success){try{memoryGraphs=JsonUtility.FromJson<MemoryGraphs>(req.downloadHandler.text);graphConnection="Category links / source-backed records";}catch(Exception){graphConnection="Invalid graph response";}}else graphConnection="Memory bridge offline";}yield return new WaitForSecondsRealtime(3);}}
 void GraphLine(Vector2 a,Vector2 b,Color color,float width){var old=GUI.matrix;var delta=b-a;GUIUtility.RotateAroundPivot(Mathf.Atan2(delta.y,delta.x)*Mathf.Rad2Deg,a);Fill(new Rect(a.x,a.y-width*.5f,delta.magnitude,width),color);GUI.matrix=old;}
 void DrawMemoryGraph(Rect panel){
 GUI.BeginGroup(panel);float w=panel.width,h=panel.height;
 Fill(new Rect(0,0,w,h),new Color(.012f,.019f,.035f));Fill(new Rect(0,0,w,1),new Color(.17f,.3f,.4f));
 var tiny=new GUIStyle(caption){fontSize=10,wordWrap=true};var detailStyle=new GUIStyle(chatBody){fontSize=11,wordWrap=true};
 GUI.Label(new Rect(14,10,w-28,22),developmentGraph?"DEVELOPMENT / CONSTELLATION":"MEMORY / CONSTELLATION",heading);
 float bw=(w-34)/2;if(GUI.Button(new Rect(12,38,bw,27),"Conversation",developmentGraph?flatButton:accentButton)){developmentGraph=false;selectedMemory="";}
 if(GUI.Button(new Rect(22+bw,38,bw,27),"Development",developmentGraph?accentButton:flatButton)){developmentGraph=true;selectedMemory="";}
 var graph=memoryGraphs==null?null:(developmentGraph?memoryGraphs.development:memoryGraphs.conversation);
 GUI.Label(new Rect(14,70,w-28,28),graphConnection+(graph!=null?" | "+graph.record_count+" records":""),tiny);
 if(graph?.nodes==null){GUI.EndGroup();return;}
 if(graphGlow==null){graphGlow=new Texture2D(48,48,TextureFormat.RGBA32,false);for(int y=0;y<48;y++)for(int x=0;x<48;x++){float r=Vector2.Distance(new Vector2(x,y),new Vector2(23.5f,23.5f))/24;graphGlow.SetPixel(x,y,new Color(1,1,1,Mathf.Exp(-r*r*7)*Mathf.Clamp01((1-r)*4)));}graphGlow.Apply();uiTextures.Add(graphGlow);}
 float bottom=135,gh=Mathf.Max(70,h-100-bottom);Vector2 center=new Vector2(w*.5f,100+gh*.5f);float radius=Mathf.Max(24,Mathf.Min(w*.34f,gh*.31f));
 var hubs=new List<MemoryGraphNode>();foreach(var n in graph.nodes)if(n.hub)hubs.Add(n);
 var positions=new Dictionary<string,Vector2>();var colors=new Dictionary<string,Color>();
 for(int i=0;i<hubs.Count;i++){
 float angle=i*Mathf.PI*2/Mathf.Max(1,hubs.Count)-Mathf.PI*.5f;var hub=hubs[i];Vector2 hp=center+new Vector2(Mathf.Cos(angle)*Mathf.Max(radius,w*.30f),Mathf.Sin(angle)*radius*.95f);positions[hub.id]=hp;Color c=Color.HSVToRGB(Mathf.Repeat((developmentGraph?.08f:.44f)+i*.09f,1),.55f,.95f);colors[hub.group]=c;
 var children=new List<MemoryGraphNode>();foreach(var n in graph.nodes)if(!n.hub&&n.group==hub.group)children.Add(n);
 for(int j=0;j<children.Count;j++){float a=j*2.399963f+i;float spread=12+Mathf.Sqrt(j+1)*7;positions[children[j].id]=hp+new Vector2(Mathf.Cos(a),Mathf.Sin(a))*spread;}
 }
 if(graph.edges!=null)foreach(var e in graph.edges)if(positions.ContainsKey(e.source)&&positions.ContainsKey(e.target))GraphLine(positions[e.source],positions[e.target],new Color(.25f,.55f,.65f,.4f),1);
 MemoryGraphNode selected=null;
 foreach(var n in graph.nodes){if(!positions.ContainsKey(n.id))continue;var pos=positions[n.id];Color c=colors[n.group];float size=n.hub?8:4;bool hover=Vector2.Distance(Event.current.mousePosition,pos)<9;bool active=selectedMemory==n.id;
 var old=GUI.color;GUI.color=new Color(c.r,c.g,c.b,active?.85f:.32f);float halo=n.hub?40:24;GUI.DrawTexture(new Rect(pos.x-halo/2,pos.y-halo/2,halo,halo),graphGlow);GUI.color=old;Fill(new Rect(pos.x-size/2,pos.y-size/2,size,size),active?Color.white:c);
 if(n.hub)GUI.Label(new Rect(pos.x-55,pos.y+8,110,30),n.label.Replace(" preference", "").Replace("historical ", ""),new GUIStyle(tiny){alignment=TextAnchor.UpperCenter});
 if(hover&&Event.current.type==EventType.MouseDown&&Event.current.button==0){selectedMemory=n.id;Event.current.Use();}
 if(active||hover)selected=n;
 }
 Fill(new Rect(10,h-bottom,w-20,bottom-10),new Color(.025f,.04f,.06f));
 if(selected!=null){GUI.Label(new Rect(20,h-bottom+8,w-40,22),selected.stage.Replace('_',' ').ToUpperInvariant(),tiny);GUI.Label(new Rect(20,h-bottom+31,w-40,65),selected.detail,detailStyle);string source=string.IsNullOrEmpty(selected.source_path)?"Select a record to inspect its source":System.IO.Path.GetFileName(selected.source_path)+(selected.source_line>0?" : line "+selected.source_line:"");GUI.Label(new Rect(20,h-30,w-40,22),source,tiny);}
 else GUI.Label(new Rect(20,h-bottom+14,w-40,90),"Select a light to inspect its record.\n\nLines show recorded category membership.\nDevelopment proposals are not lived experiences.",detailStyle);
 GUI.EndGroup();
 }
 }
}
