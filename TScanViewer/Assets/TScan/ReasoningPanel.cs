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
   GUI.Label(new Rect(16,10,width-100,27),"Steve's thinking",heading);
   if(GUI.Button(new Rect(width-78,8,62,28),"Stop",flatButton))DashboardBody?.GetComponent<SteveBridge>()?.Pause();
   string phase=current.reasoningActive?"Thinking…":current.status=="generating"?"Waiting for thinking output…":string.IsNullOrEmpty(CurrentReasoningText)?"No thinking text received yet":"Last decision";
   GUI.Label(new Rect(16,42,width-32,24),phase+(current.reasoningTokens>0?" · "+current.reasoningTokens.ToString("N0")+" thinking tokens reported":""),caption);
   Fill(new Rect(16,72,width-32,1),new Color(.09f,.13f,.16f));
   if(reasoningStyle==null)reasoningStyle=new GUIStyle(chatBody){richText=false};
   string text=CurrentReasoningText;
   if(string.IsNullOrEmpty(text))text=current.reasoningTokens>0?"The provider reported thinking tokens but supplied no thinking text.":"Thinking will stream here when Steve makes his next decision.";
   float viewHeight=Mathf.Max(30,height-92),textWidth=width-54;
   float contentHeight=Mathf.Max(viewHeight,reasoningStyle.CalcHeight(new GUIContent(text),textWidth)+12);
   if(reasoningRequest!=(current.requestId??"")){reasoningRequest=current.requestId??"";reasoningScroll=Vector2.zero;reasoningContentHeight=0;}
   bool follow=reasoningScroll.y>=Mathf.Max(0,reasoningContentHeight-viewHeight)-24;
   if(follow&&contentHeight>reasoningContentHeight)reasoningScroll.y=Mathf.Max(0,contentHeight-viewHeight);
   reasoningContentHeight=contentHeight;
   reasoningScroll=GUI.BeginScrollView(new Rect(14,82,width-28,viewHeight),reasoningScroll,new Rect(0,0,textWidth+4,contentHeight));
   GUI.Label(new Rect(2,0,textWidth,contentHeight),text,reasoningStyle);GUI.EndScrollView();
  }
 }
}
