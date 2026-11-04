using UnityEngine;

namespace Steve.TScan {

 public sealed partial class TScanViewer {

  void DrawGridRun(GridWorkbench grid){

   var box=RunStatusPanel;Fill(box,new Color(.018f,.029f,.039f));GUI.BeginGroup(box);float w=box.width;var s=grid.State;

   GUI.Label(new Rect(14,10,w-180,25),"CURRENT RUN",heading);

   GUI.enabled=s!=null&&!grid.Busy&&!sending&&(latestFrame??frame).status!="generating";

   if(GUI.Button(new Rect(w-166,8,82,28),new GUIContent("Position","Reset only Steve's position. Use Reset above chat to archive and reset the whole run."),flatButton))grid.ResetFixture();GUI.enabled=true;

   if(GUI.Button(new Rect(w-76,8,62,28),"Stop",flatButton))DashboardBody.GetComponent<SteveBridge>().Pause();

   if(s!=null){

    GUI.Label(new Rect(16,53,w-32,35),s.running?"Continuing from action feedback. Steve can call complete to finish.":"Paused"+(s.decision_loop?.pause_reason=="complete"?" Â· complete called":s.decision_loop?.pause_reason=="no_action"?" Â· no action requested":"")+". A new chat message wakes the loop.",chatBody);

    GUI.Label(new Rect(16,100,w-32,32),$"Position x={s.self.col}, y={s.self.row} Â· facing {s.self.facing} Â· {grid.PresentationState}   /   revision {s.world_revision} Â· observation {s.observation_seq}",caption);

    var r=s.last_action;if(!string.IsNullOrEmpty(r?.action_id))GUI.Label(new Rect(16,142,w-32,60),$"{r.action} â†’ {r.outcome}\nAdmission {r.decision} Â· presentation {r.presentation_status} Â· {r.action_id}",muted);

    if(!string.IsNullOrEmpty(grid.Error))GUI.Label(new Rect(16,210,w-32,60),grid.Error,muted);

   }else {
    GUI.Label(new Rect(16,55,w-32,50),"Meadow loaded locally. Waiting for the movement backendâ€¦",muted);
    if(!string.IsNullOrEmpty(grid.Error))GUI.Label(new Rect(16,115,w-32,65),grid.Error,muted);
   }

   GUI.EndGroup();

  }

 }

}

