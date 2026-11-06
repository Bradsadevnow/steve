using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 [DefaultExecutionOrder(100)]
 public sealed class SteveBody : MonoBehaviour {
  public Camera BodyCamera {get;private set;}
  public AvatarCameraRig EnvironmentCamera {get;private set;}
  public GridWorkbench Bench {get;private set;}
  public Transform AvatarTransform=>avatar?avatar.transform:null;
  public bool RigReady=>Bench!=null&&avatar!=null;
  TScanViewer viewer;GameObject avatar;
  readonly List<GameObject> lights=new List<GameObject>();
  const int AvatarLayer=30;
  void Start(){
   if(Resources.Load<TextAsset>("Meadow/hover")==null)throw new InvalidOperationException("Missing Meadow/hover art");
   avatar=new GameObject("Steve / Hover meadow");avatar.transform.SetParent(transform,false);avatar.transform.position=new Vector3(200,0,0);
   Bench=avatar.AddComponent<GridWorkbench>();Bench.Initialize();
   viewer=FindAnyObjectByType<TScanViewer>();
   var go=new GameObject("Steve Avatar Camera");go.transform.SetParent(transform);
   BodyCamera=go.AddComponent<Camera>();BodyCamera.cullingMask=1<<AvatarLayer;BodyCamera.depth=2;
   BodyCamera.clearFlags=CameraClearFlags.SolidColor;BodyCamera.backgroundColor=new Color(.013f,.025f,.035f);
   BodyCamera.orthographic=true;BodyCamera.nearClipPlane=.1f;BodyCamera.farClipPlane=150;
   EnvironmentCamera=go.AddComponent<AvatarCameraRig>();EnvironmentCamera.Configure(avatar.transform);EnvironmentCamera.ConfigureMeadow(avatar.transform);
   AddLight("Avatar key",new Vector3(-5,7,-7),new Color(1,.88f,.76f),1.2f);
   AddLight("Avatar fill",new Vector3(5,4,-3),new Color(.65f,.85f,1),.7f);
   AddLight("Avatar rim",new Vector3(1,6,5),new Color(.5f,1,.8f),1);
  }
  void AddLight(string label,Vector3 offset,Color color,float intensity){
   var go=new GameObject(label);go.transform.SetParent(transform);go.transform.position=avatar.transform.position+offset;
   go.transform.LookAt(avatar.transform.position+Vector3.up*2.5f);
   var light=go.AddComponent<Light>();light.type=LightType.Spot;light.spotAngle=105;light.range=14;
   light.intensity=intensity*12;light.color=color;light.cullingMask=1<<AvatarLayer;light.shadows=LightShadows.None;lights.Add(go);
  }
  void LateUpdate(){
   if(!RigReady||BodyCamera==null)return;
   if(viewer!=null)BodyCamera.rect=viewer.EnvironmentViewport;
  }
  void OnDestroy(){if(BodyCamera!=null)Destroy(BodyCamera.gameObject);foreach(var light in lights)if(light!=null)Destroy(light);}
 }
}
