using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  [Serializable] class SelfRecord {public string statement,reason;}
  [Serializable] class SelfPosition {public int x,y;public string facing;public bool current;}
  [Serializable] class SelfFocus {public string task_id,title,reason,status,goal_id;}
  [Serializable] class SelfGoal {public string id,statement,reason,status;public bool linked_to_focus;}
  [Serializable] class SelfTaskRow {public string id,title,status;public bool in_focus;}
  [Serializable] class SelfTask {public string id,title,status;}
  [Serializable] class SelfExperience {public string id,summary,status,outcome;}
  [Serializable] class SelfAttempts {public int total,moved,blocked;}
  [Serializable] class SelfView {
   public string activity;public SelfPosition position;public SelfFocus focus;
   public SelfTask[] unfinished,finished;public SelfGoal[] goals;public SelfTaskRow[] tasks;public string status_note;public SelfRecord[] commitments,assessments,beliefs;
   public string[] capabilities;public SelfExperience[] recent;public SelfAttempts attempts;
  }
  SelfView selfView;
  string selfError="";Vector2 selfScroll;
  float selfContentHeight=600;

  IEnumerator PollSelf(){while(true){using(var req=UnityWebRequest.Get(Endpoint+"/self-view")){
   req.timeout=5;yield return req.SendWebRequest();
   if(req.result==UnityWebRequest.Result.Success){selfView=JsonUtility.FromJson<SelfView>(req.downloadHandler.text);selfError="";}
   else selfError=req.error;
  }yield return new WaitForSecondsRealtime(1);}}

  void DrawSelf(float width,float height){
   GUI.Label(new Rect(20,60,width-120,28),"Self state",heading);
   GUI.Label(new Rect(width-96,65,76,20),selfView?.activity??"Connecting",caption);
   float w=width-58,y=0;
   selfScroll=GUI.BeginScrollView(new Rect(18,102,width-26,height-114),selfScroll,new Rect(0,0,w,Mathf.Max(height-114,selfContentHeight)));
   void Text(string value,GUIStyle style){if(string.IsNullOrEmpty(value))return;float h=style.CalcHeight(new GUIContent(value),w);GUI.Label(new Rect(0,y,w,h),value,style);y+=h+10;}
   void Section(string label){y+=12;Fill(new Rect(0,y,w,1),new Color(.08f,.16f,.19f));y+=12;Text(label,caption);}
   void Record(SelfRecord record){
    Text(record.statement,chatBody);
    if(!string.IsNullOrEmpty(record.reason))Text(record.reason,muted);
   }
   if(selfView==null){Text("Connecting…",muted);}
   else{
    var position=selfView.position;
    if(position!=null){Text(position.current?"Here":"Last position",caption);Text($"({position.x}, {position.y}) · {position.facing}",chatBody);}
    Section("Goal");
    if(selfView.goals==null||selfView.goals.Length==0)Text("No goal recorded yet.",muted);
    else foreach(var goal in selfView.goals){
     Text(goal.status,caption);Text(goal.statement,chatBody);
     if(!string.IsNullOrEmpty(goal.reason))Text(goal.reason,muted);
     if(goal.linked_to_focus)Text("The task in focus serves this goal.",muted);
    }
    Section("Tasks");
    if(selfView.tasks==null||selfView.tasks.Length==0)Text("No tasks yet.",muted);
    else foreach(var task in selfView.tasks){
     string mark=task.status=="completed"?"[x]":task.status=="in_progress"?"[~]":"[ ]";
     Text((task.in_focus?"> ":"  ")+mark+" "+task.title,chatBody);
     if(task.in_focus&&!string.IsNullOrEmpty(selfView.focus?.reason))Text(selfView.focus.reason,muted);
    }
    if(!string.IsNullOrEmpty(selfView.status_note))Text(selfView.status_note,muted);
    if(selfView.commitments!=null&&selfView.commitments.Length>0){
     Section("Commitments that persist");foreach(var record in selfView.commitments)Record(record);
    }
    Section("Self-assessments");
    if(selfView.assessments==null||selfView.assessments.Length==0)Text("None recorded yet.",muted);
    else foreach(var record in selfView.assessments)Record(record);
    Section("Beliefs");
    if(selfView.beliefs==null||selfView.beliefs.Length==0)Text("None recorded yet.",muted);
    else foreach(var record in selfView.beliefs)Record(record);
    Section("Recent experience");
    if(selfView.attempts?.total>0)Text($"{selfView.attempts.moved} moves · {selfView.attempts.blocked} blocked this run",muted);
    if(selfView.recent==null||selfView.recent.Length==0)Text("Nothing new recorded.",muted);
    else foreach(var experience in selfView.recent)Text(experience.summary,chatBody);
    Section("Capabilities");foreach(var capability in selfView.capabilities??Array.Empty<string>())Text("• "+capability,muted);
   }
   if(!string.IsNullOrEmpty(selfError))Text("Connection interrupted. Showing the last state.",muted);
   selfContentHeight=y+20;GUI.EndScrollView();
  }
 }
}
