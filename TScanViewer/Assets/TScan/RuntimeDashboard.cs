using UnityEngine;
namespace Steve.TScan {
 public sealed partial class TScanViewer {
  int rightTab=1;
  SteveBody DashboardBody=>FindAnyObjectByType<SteveBody>();
  float LedgerHeight=>Mathf.Clamp(CanvasHeight*.27f,225,275);
  Rect LedgerPanel=>new Rect(LeftWidth+8,CanvasHeight-LedgerHeight,CanvasWidth-LeftWidth-RightWidth-16,LedgerHeight-8);
  void DrawRunDashboard(){var box=LedgerPanel;Fill(box,new Color(.018f,.029f,.039f));GUI.BeginGroup(box);DrawReasoning(box.width,box.height);GUI.EndGroup();}
  void DrawDashboardRight(float x,float width,float height){
   float top=8;height-=top;GUI.BeginGroup(new Rect(x,top,width,height));
   rightTab=GUI.SelectionGrid(new Rect(12,12,width-24,30),rightTab,new[]{"Activity","Self","View"},3,compactButton);
   if(rightTab==2){GUI.BeginGroup(new Rect(0,48,width,height-48));DrawControls(0,width,height-48);GUI.EndGroup();}
   else if(rightTab==1)DrawSelf(width,height);else DrawBodyActivity(width,height);
   GUI.EndGroup();
  }
  void DrawDashboardLeft(float width,float height)=>DrawChat(width,height);
 }
}
