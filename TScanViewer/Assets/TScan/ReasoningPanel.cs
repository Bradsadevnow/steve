using UnityEngine;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  Vector2 reasoningScroll;
  string reasoningRequest="";
  float reasoningContentHeight;
  GUIStyle reasoningStyle;
  public string CurrentReasoningText=>(latestFrame??frame).reasoningText??"";
  void DrawReasoning(float width,float height){
   var current=latestFrame??frame;
   GUI.Label(new Rect(20,60,width-40,27),"Steve's thinking",heading);
   string phase=current.reasoningActive?"Thinking…":current.status=="generating"?"Waiting for thinking output…":string.IsNullOrEmpty(CurrentReasoningText)?"No thinking text received yet":"Last decision";
   GUI.Label(new Rect(20,94,width-40,40),phase+"\n"+(current.reasoningTokens>0?current.reasoningTokens.ToString("N0")+" thinking tokens reported":"Live model stream"),caption);
   GUI.Label(new Rect(20,140,width-40,40),"Model reasoning for the current decision.",muted);
   Fill(new Rect(20,184,width-40,1),new Color(.09f,.13f,.16f));
   if(reasoningStyle==null)reasoningStyle=new GUIStyle(chatBody){richText=false};
   string text=CurrentReasoningText;
   if(string.IsNullOrEmpty(text))text=current.reasoningTokens>0?"The provider reported thinking tokens but supplied no thinking text.":"Thinking will stream here when Steve makes his next decision.";
   float viewHeight=Mathf.Max(30,height-214),textWidth=width-58;
   float contentHeight=Mathf.Max(viewHeight,reasoningStyle.CalcHeight(new GUIContent(text),textWidth)+12);
   if(reasoningRequest!=(current.requestId??"")){reasoningRequest=current.requestId??"";reasoningScroll=Vector2.zero;reasoningContentHeight=0;}
   bool follow=reasoningScroll.y>=Mathf.Max(0,reasoningContentHeight-viewHeight)-24;
   if(follow&&contentHeight>reasoningContentHeight)reasoningScroll.y=Mathf.Max(0,contentHeight-viewHeight);
   reasoningContentHeight=contentHeight;
   reasoningScroll=GUI.BeginScrollView(new Rect(18,202,width-30,viewHeight),reasoningScroll,new Rect(0,0,textWidth+4,contentHeight));
   GUI.Label(new Rect(2,0,textWidth,contentHeight),text,reasoningStyle);GUI.EndScrollView();
  }
 }
}
