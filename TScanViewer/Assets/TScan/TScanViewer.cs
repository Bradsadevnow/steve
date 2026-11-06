using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 [Serializable] public class ScanFrame {
  public int index,tokenId,generatedTokens,reasoningTokens;
  public string source,status,token,text,error,requestId,requestKind,reasoningText,reasoningToken;
  public bool reasoningActive;
  public string[] cancelledRequests;
 }
 [DefaultExecutionOrder(300)]
 public sealed partial class TScanViewer : MonoBehaviour {
  public string Endpoint="http://127.0.0.1:8765";
  public int ReceivedFrames;
  public string Connection="CONNECTING";
  ScanFrame frame=new ScanFrame();
  bool cinema;string prompt="";
  void Start(){
   Application.runInBackground=true;Application.targetFrameRate=60;
   foreach(var camera in FindObjectsByType<Camera>(FindObjectsSortMode.None))if(camera.GetComponentInParent<SteveBody>()==null)camera.gameObject.SetActive(false);
   LoadAppliedWorld();StartCoroutine(PollMemoryGraphs());StartCoroutine(RestoreChat());
   StartCoroutine(PollSelf());StartCoroutine(Poll());
  }
  IEnumerator Poll(){while(true){
   using(var req=UnityWebRequest.Get(Endpoint+"/frame")){
    req.timeout=3;yield return req.SendWebRequest();
    if(req.result==UnityWebRequest.Result.Success){
     try{var next=JsonUtility.FromJson<ScanFrame>(req.downloadHandler.text);frame=next;latestFrame=next;Connection="CONNECTED";ReceivedFrames++;UpdateChatStream(next);}
     catch(Exception e){Connection="INVALID FRAME: "+e.Message;}
    }else Connection="BRIDGE OFFLINE";
   }
   yield return new WaitForSecondsRealtime(.1f);
  }}
  void Update(){HandleCameraInput();UpdateBuilder();UpdateShell();}
  void LateUpdate(){ShellLateUpdate();}
        IEnumerator Generate(){
            string submitted=prompt.Trim();if(submitted.Length==0||sending)yield break;
            chat.Add(new ChatLine("user",submitted));pendingChat=new ChatLine("assistant","");chat.Add(pendingChat);
            autoFollowChat=true;prompt="";sending=true;activeRequest="";
            var escaped=JsonUtility.ToJson(new PromptRequest{prompt=submitted});
            using(var req=new UnityWebRequest(Endpoint+"/generate","POST")){
                req.uploadHandler=new UploadHandlerRaw(Encoding.UTF8.GetBytes(escaped));req.downloadHandler=new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type","application/json");req.timeout=5;yield return req.SendWebRequest();
                if(req.result!=UnityWebRequest.Result.Success){pendingChat.text="Request failed: "+req.downloadHandler.text;pendingChat.failed=true;sending=false;}
                else {activeRequest=JsonUtility.FromJson<AcceptedRequest>(req.downloadHandler.text).requestId;UpdateChatStream(latestFrame??frame);}
            }
        }
        [Serializable] class PromptRequest {public string prompt;}
        [Serializable] class AcceptedRequest {public string requestId;}

  void OnDestroy(){foreach(var texture in uiTextures)if(texture)Destroy(texture);}
 }
}
