using System;
using System.Linq;
using UnityEngine;

namespace Steve.TScan {
 // Cosmetic, confirmed-loadout portrait. Dedicated layer; no scene or gameplay state writes.
 public sealed class CharacterPortrait:IDisposable {
  GameObject stage,model;Camera camera;RenderTexture texture;string key="";
  public RenderTexture Texture=>texture;
  public void Update(CharacterState state,Transform owner,bool visible){
   if(state==null)return;
   if(!stage){
    // Managed views are recreated on script reload; reclaim only this view's owned studio.
    PreviewStudioLifetime.Reclaim(owner,"Confirmed character portrait");
    stage=new GameObject("Confirmed character portrait"){hideFlags=HideFlags.DontSave};stage.transform.SetParent(owner,false);stage.transform.position=new Vector3(1000,-300,0);
    var go=new GameObject("Portrait camera"){hideFlags=HideFlags.DontSave};go.transform.SetParent(stage.transform,false);camera=go.AddComponent<Camera>();
    camera.cullingMask=1<<28;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.035f,.055f,.065f);camera.orthographic=true;camera.nearClipPlane=.01f;camera.farClipPlane=30;
    texture=new RenderTexture(160,160,24){name="Confirmed Steve portrait",hideFlags=HideFlags.DontSave};camera.targetTexture=texture;
   }
   camera.enabled=visible;
   var next=CharacterCatalog.VisualKey(state);
   if(next==key&&model)return;key=next;
   if(model){model.SetActive(false);UnityEngine.Object.Destroy(model);}
   model=CharacterCatalog.Create(state,stage.transform,28);model.transform.localRotation=Quaternion.Euler(0,12,0);
   var renderers=model.GetComponentsInChildren<Renderer>();if(renderers.Length==0)return;
   var bounds=renderers[0].bounds;foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
   camera.transform.position=bounds.center+Vector3.back*8;camera.transform.rotation=Quaternion.identity;camera.orthographicSize=Mathf.Max(bounds.extents.x,bounds.extents.y)*1.12f;
  }
  public void Dispose(){PreviewStudioLifetime.Release(stage);stage=null;model=null;camera=null;texture=null;key="";}
 }
}
