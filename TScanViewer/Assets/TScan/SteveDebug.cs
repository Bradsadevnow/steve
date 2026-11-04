using UnityEngine;
namespace Steve.TScan {
 [RequireComponent(typeof(SteveBody),typeof(SteveBridge))]
 public sealed class SteveDebug:MonoBehaviour {
  public float Draw(float x,float y,float width,GUIStyle button,GUIStyle text,GUIStyle title){
   var grid=GetComponent<SteveBody>().Bench;
   GUI.Label(new Rect(x,y,width,24),"STEVE / MEADOW",title);y+=30;
   if(GUI.Button(new Rect(x,y,width,36),"Stop",button))GetComponent<SteveBridge>().Pause();y+=44;
   var state=grid?.State;
   GUI.Label(new Rect(x,y,width,100),state==null?"Waiting for backend":$"Position ({state.self.col}, {state.self.row}) / {state.self.facing}\n{grid.PresentationState} / {grid.Error}",text);
   return y+110;
  }
 }
}
