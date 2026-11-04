using UnityEngine;
namespace Steve.TScan {
 [DefaultExecutionOrder(200)]
 public sealed class AvatarCameraRig:MonoBehaviour {
  public bool OrbitEnabled;
  public float Yaw=25,Pitch=12,Zoom=3;
  public Vector3 Target {get;private set;}
  Transform actor;Camera eye;Vector3 center;float fittedZoom,fittedWidth;
  public void Configure(Transform avatar){
   actor=avatar;eye=GetComponent<Camera>();eye.orthographic=true;eye.farClipPlane=150;
   var renderers=actor.GetComponentsInChildren<Renderer>();var bounds=new Bounds(actor.position,Vector3.one);
   foreach(var r in renderers)bounds.Encapsulate(r.bounds);
   center=bounds.center;fittedWidth=bounds.extents.x*1.3f;fittedZoom=Mathf.Max(1.5f,bounds.extents.y*1.3f);ResetView();
  }
  public void ConfigureMeadow(Transform avatar){actor=avatar;center=avatar.position;fittedWidth=12;fittedZoom=12;ResetView();Pitch=50;}
  public void ResetView(){Target=center;Yaw=25;Pitch=12;Zoom=fittedZoom;OrbitEnabled=false;}
  public void FocusActor()=>ResetView();
  public void ApplyGesture(Vector2 delta,float scroll,bool pan){
   if(OrbitEnabled)return;
   if(pan){var rotation=Quaternion.Euler(Pitch,Yaw,0);float units=2*Zoom/Mathf.Max(1,eye.pixelHeight);Target-=rotation*Vector3.right*delta.x*units+rotation*Vector3.up*delta.y*units;}
   else{Yaw+=delta.x*.18f;Pitch=Mathf.Clamp(Pitch-delta.y*.18f,10,80);}
   Zoom=Mathf.Clamp(Zoom*Mathf.Exp(-scroll*.14f),.5f,30);
  }
  public object State()=>new{orbit=OrbitEnabled,yaw=Yaw,pitch=Pitch,zoom=Zoom,target=Target,viewport=eye.rect};
  void LateUpdate(){if(actor==null)return;if(OrbitEnabled)Yaw+=Time.unscaledDeltaTime*8;eye.orthographicSize=Zoom*Mathf.Max(1,fittedWidth/(fittedZoom*Mathf.Max(.1f,eye.aspect)));transform.position=Target+Quaternion.Euler(Pitch,Yaw,0)*new Vector3(0,0,-50);transform.LookAt(Target);}
 }
}
