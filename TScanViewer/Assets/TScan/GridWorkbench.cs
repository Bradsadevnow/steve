using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.Rendering;
namespace Steve.TScan {
 [Serializable] public class GridAvatar {public string id,facing;public int col,row;}
 [Serializable] public class GridLandmark {public string id,name,color,kind;public int col,row;public bool occupiable;}
 [Serializable] public class GridDecisionLoop {public bool active;public string origin_request_id,pause_reason;}
 [Serializable] public class GridReceipt {public string action_id,action,outcome,decision,presentation_status,facing_before,facing_after;public int[] position_before,position_after;public int world_revision,observation_seq;}
 [Serializable] public class GridSnapshot {public string session_id,observation_id,world_manifest_hash;public int observation_seq,world_revision;public GridAvatar self;public GridReceipt last_action,presentation;public bool enabled,running,world_ready;public GridLandmark[] visible_targets;public string[] standing_on;public GridDecisionLoop decision_loop;}
 public sealed class GridWorkbench:MonoBehaviour {
  [Serializable] class Part {public string name,key;public float[] vertices,normals,colors;public int[] triangles;}
  [Serializable] class Art {public Part[] parts;}
  [Serializable] class Client {public string client_id,manifest_hash;}
  [Serializable] class Registration {public string client_id;public MeadowManifest manifest;}
  [Serializable] class Ack {public string client_id,action_id,session_id;}
  [Serializable] class Control {public string action;}
  public GridSnapshot State;public string PresentationState="IDLE",Error="";
  bool HasPresentation=>!string.IsNullOrEmpty(State?.presentation?.action_id);
  public bool Ready=>State!=null&&State.world_ready&&string.IsNullOrEmpty(Error);public bool Busy=>animating||HasPresentation;
  public Transform Tool=>visual;public Vector3 Destination=>visual?visual.position:transform.position;
  Transform visual,head,shadow;string client=Guid.NewGuid().ToString("N"),session="",active="",done="";bool animating;Material material;
  readonly List<Mesh> meshes=new List<Mesh>();readonly List<Transform> eyes=new List<Transform>();
  MeadowEnvironment environment;string publishedManifest="",manifestHash="";
  string Endpoint=>FindAnyObjectByType<SteveBridge>().Endpoint;
  static Vector3 Cell(int col,int row)=>MeadowEnvironment.Cell(col,row);
  Mesh MakeMesh(Part p,Vector3 offset){var m=new Mesh{name=p.name,indexFormat=IndexFormat.UInt32};var v=new Vector3[p.vertices.Length/3];var n=new Vector3[v.Length];var c=new Color[v.Length];for(int i=0;i<v.Length;i++){v[i]=new Vector3(p.vertices[3*i],p.vertices[3*i+1],p.vertices[3*i+2])-offset;n[i]=new Vector3(p.normals[3*i],p.normals[3*i+1],p.normals[3*i+2]);c[i]=new Color(p.colors[4*i],p.colors[4*i+1],p.colors[4*i+2],p.colors[4*i+3]);}m.vertices=v;m.normals=n;m.colors=c;m.triangles=p.triangles;m.RecalculateBounds();meshes.Add(m);return m;}
  GameObject Render(string name,Transform parent,Mesh mesh){var o=new GameObject(name);o.layer=30;o.transform.SetParent(parent,false);o.AddComponent<MeshFilter>().sharedMesh=mesh;o.AddComponent<MeshRenderer>().sharedMaterial=material;return o;}
  public void Initialize(){
   environment=FindAnyObjectByType<MeadowEnvironment>();
   if(!environment||!environment.definition)throw new InvalidOperationException("Scene requires a MeadowEnvironment with an authored world definition");
   transform.SetPositionAndRotation(environment.transform.position,environment.transform.rotation);
   transform.localScale=environment.transform.lossyScale;
   material=new Material(Shader.Find("Steve/MeadowVertex"));
   var art=JsonUtility.FromJson<Art>(Resources.Load<TextAsset>("Meadow/hover").text);visual=new GameObject("HoverVisual").transform;visual.SetParent(transform,false);head=new GameObject("Expressive head").transform;head.SetParent(visual,false);head.localPosition=Vector3.up*1.15f;
   foreach(var p in art.parts){bool face=!p.name.StartsWith("POD /");var part=Render(p.name,face?head:visual,MakeMesh(p,face?Vector3.up*1.15f:Vector3.zero));if(p.name.Contains("pupil")||p.name.Contains("iris")||p.name.Contains("catchlight"))eyes.Add(part.transform);}
   visual.localPosition=Cell(environment.definition.manifest.spawn.col,environment.definition.manifest.spawn.row);visual.localRotation=Quaternion.Euler(0,Yaw("north"),0);
   var s=GameObject.CreatePrimitive(PrimitiveType.Quad);s.name="Hover floor shadow";s.layer=30;Destroy(s.GetComponent<Collider>());shadow=s.transform;shadow.SetParent(transform,false);shadow.localRotation=Quaternion.Euler(90,0,0);shadow.localScale=new Vector3(1.05f,.8f,1);var sm=new Material(Shader.Find("Steve/HoverShadow"));sm.SetColor("_BaseColor",new Color(.04f,.09f,.07f,.3f));s.GetComponent<Renderer>().material=sm;
   StartCoroutine(Poll());
  }
  IEnumerator Post(string route,object data,Action<string> success=null){using(var req=new UnityWebRequest(Endpoint+route,"POST")){req.uploadHandler=new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(JsonUtility.ToJson(data)));req.downloadHandler=new DownloadHandlerBuffer();req.SetRequestHeader("Content-Type","application/json");req.timeout=5;yield return req.SendWebRequest();if(req.result==UnityWebRequest.Result.Success){Error="";success?.Invoke(req.downloadHandler.text);}else Error=string.IsNullOrEmpty(req.downloadHandler.text)?req.error:req.downloadHandler.text;}}
  IEnumerator Poll(){while(true){
   var definition=environment.definition.ManifestJson;
   GridSnapshot received=null;
   if(publishedManifest!=definition||string.IsNullOrEmpty(manifestHash)){
    yield return Post("/grid/world",new Registration{client_id=client,manifest=environment.definition.manifest},text=>received=JsonUtility.FromJson<GridSnapshot>(text));
    if(received!=null&&received.world_ready&&!string.IsNullOrEmpty(received.world_manifest_hash)){publishedManifest=definition;manifestHash=received.world_manifest_hash;}
    // The backend remembers the highest revision it confirmed. If this definition is older and different, publish it as a newer revision rather than leaving the builder stuck.
    else if(received==null&&Error.Contains("higher revision")){environment.definition.manifest.revision++;WorldBuilder.SaveCurrent(environment.definition.manifest);Error="";}
   }else yield return Post("/grid/poll",new Client{client_id=client,manifest_hash=manifestHash},text=>received=JsonUtility.FromJson<GridSnapshot>(text));
   if(received==null||!received.world_ready){manifestHash="";State=null;yield return new WaitForSecondsRealtime(1);continue;}
   State=received;
   if(session!=State.session_id){session=State.session_id;done="";active="";visual.localPosition=Cell(State.self.col,State.self.row);visual.localRotation=Quaternion.Euler(0,Yaw(State.self.facing),0);}
   if(HasPresentation&&!animating){if(State.presentation.action_id==done)yield return AckStep(done);else yield return Animate(State.presentation);}
   if(!animating&&!HasPresentation)visual.localPosition=Cell(State.self.col,State.self.row);
   yield return new WaitForSecondsRealtime(.08f);}}
  static float Yaw(string f)=>f=="north"?180:f=="east"?270:f=="west"?90:0;
  IEnumerator AckStep(string id)=>Post("/grid/ack",new Ack{client_id=client,action_id=id,session_id=session});
  IEnumerator Animate(GridReceipt r){
   animating=true;active=r.action_id;var a=Cell(r.position_before[0],r.position_before[1]);var b=Cell(r.position_after[0],r.position_after[1]);var from=visual.localRotation;var to=Quaternion.Euler(0,Yaw(r.facing_after),0);float elapsed=0,duration=r.outcome=="moved"?.54f:.25f;
   while(elapsed<duration){elapsed+=Time.unscaledDeltaTime;float orient=Mathf.Clamp01(elapsed/.12f);float lead=Mathf.Clamp(Mathf.DeltaAngle(from.eulerAngles.y,to.eulerAngles.y)*(1-orient),-45,45);head.localRotation=Quaternion.Euler(0,lead,0);foreach(var eye in eyes)eye.localPosition=Vector3.right*Mathf.Sin(lead*Mathf.Deg2Rad)*.025f;visual.localRotation=Quaternion.Slerp(from,to,Mathf.SmoothStep(0,1,orient));
    if(r.outcome=="moved"){PresentationState=elapsed<.12f?"ORIENTING":elapsed<.42f?"MOVING":"SETTLING";float t=Mathf.Clamp01((elapsed-.12f)/.3f);visual.localPosition=Vector3.Lerp(a,b,Mathf.SmoothStep(0,1,t));visual.localRotation*=Quaternion.Euler(Mathf.Sin(t*Mathf.PI)*-7,0,0);}
    else {PresentationState="BLOCKED";visual.localPosition=a;visual.localRotation*=Quaternion.Euler(-Mathf.Sin(elapsed/duration*Mathf.PI)*6,0,0);}
    yield return null;
   }
   visual.localPosition=b;visual.localRotation=to;head.localRotation=Quaternion.identity;foreach(var eye in eyes)eye.localPosition=Vector3.zero;PresentationState="IDLE";done=r.action_id;animating=false;yield return AckStep(done);
  }
  void LateUpdate(){if(visual==null)return;var p=visual.localPosition;shadow.localPosition=new Vector3(p.x,.026f,p.z);var meshY=.035f*Mathf.Sin(Time.unscaledTime*Mathf.PI);visual.localPosition=new Vector3(p.x,meshY,p.z);}
  public void Resume()=>StartCoroutine(Post("/grid/control",new Control{action="start"}));
  public void Stop()=>StartCoroutine(Post("/grid/control",new Control{action="stop"}));
  public void ResetFixture(){FindAnyObjectByType<SteveBridge>().Pause();StartCoroutine(Post("/grid/control",new Control{action="reset"}));}
  void OnDestroy(){foreach(var m in meshes)Destroy(m);if(material)Destroy(material);}
 }
}
