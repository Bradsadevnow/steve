using UnityEngine;
namespace Steve.TScan {
 public sealed partial class TScanViewer {
  int rightTab;
  SteveBody DashboardBody=>FindAnyObjectByType<SteveBody>();
  float LedgerHeight=>Mathf.Clamp(CanvasHeight*.27f,225,275);
  Rect LedgerPanel=>new Rect(LeftWidth+8,CanvasHeight-LedgerHeight,CanvasWidth-LeftWidth-RightWidth-16,LedgerHeight-8);
  void DrawRunDashboard(){if(DashboardBody?.Bench is GridWorkbench grid){DrawGridRun(grid);DrawOperatorNotes();}}
  void DrawDashboardRight(float x,float width,float height){
   float top=8;height-=top;GUI.BeginGroup(new Rect(x,top,width,height));
   rightTab=GUI.SelectionGrid(new Rect(12,12,width-24,30),rightTab,new[]{"Thinking","Activity","View"},3,compactButton);
   if(rightTab==2){GUI.BeginGroup(new Rect(0,48,width,height-48));DrawControls(0,width,height-48);GUI.EndGroup();}
   else if(rightTab==1)DrawBodyActivity(width,height);else DrawReasoning(width,height);
   GUI.EndGroup();
  }
  void DrawDashboardLeft(float width,float height)=>DrawChat(width,height);
 }
}
