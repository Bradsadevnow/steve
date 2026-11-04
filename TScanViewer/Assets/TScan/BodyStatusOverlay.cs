using UnityEngine;
namespace Steve.TScan {
 public sealed partial class TScanViewer {
  void DrawBodyActivity(float width,float height){
   var grid=DashboardBody?.Bench;var state=grid?.State;
   GUI.Label(new Rect(20,60,width-40,28),"Activity",heading);
   GUI.Label(new Rect(20,100,width-40,55),state==null?"Waiting for backend":state.running?"Steve is continuing.":"Steve is idle.",chatBody);
   var receipt=state?.last_action;
   if(receipt!=null)GUI.Label(new Rect(20,160,width-40,150),$"LAST ACTION RESULT\n{receipt.action} → {receipt.outcome}\nAdmission {receipt.decision}\nPresentation {receipt.presentation_status}",muted);
   if(!string.IsNullOrEmpty(grid?.Error))GUI.Label(new Rect(20,330,width-40,height-340),grid.Error,muted);
  }
 }
}
