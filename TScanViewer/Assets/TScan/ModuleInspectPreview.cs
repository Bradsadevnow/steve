using System;
using UnityEngine;
namespace Steve.TScan {
 // One cosmetic studio, active only while an item card is visible.
 public sealed class ModuleInspectPreview:IDisposable {
  GameObject stage,pivot;Camera camera;RenderTexture texture;Material material;Quaternion orientation;float yaw;string key="";
  public RenderTexture Texture=>texture;
  public void Show(CharacterModule module,Transform owner){
   if(!stage){
    PreviewStudioLifetime.Reclaim(owner,"Module inspection studio",true);
    stage=new GameObject("Module inspection studio"){hideFlags=HideFlags.DontSave};stage.transform.SetParent(owner,false);stage.transform.position=new Vector3(1600,-500,0);
    var go=new GameObject("Item camera");go.transform.SetParent(stage.transform,false);camera=go.AddComponent<Camera>();camera.orthographic=true;camera.aspect=320f/240;camera.cullingMask=1<<26;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.035f,.05f,.065f);camera.nearClipPlane=.01f;camera.farClipPlane=30;camera.transform.localPosition=Vector3.back*8;
    texture=new RenderTexture(320,240,24){name="Rotating module inspection",hideFlags=HideFlags.DontSave};camera.targetTexture=texture;
    var lightGo=new GameObject("Item light");lightGo.transform.SetParent(stage.transform,false);lightGo.transform.localRotation=Quaternion.Euler(30,-30,0);var light=lightGo.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.2f;light.cullingMask=1<<26;
    material=new Material(Shader.Find("Steve/MeadowVertex")){hideFlags=HideFlags.DontSave};
   }
   camera.enabled=true;if(key==module.id&&pivot)return;key=module.id;
   if(pivot){pivot.SetActive(false);UnityEngine.Object.Destroy(pivot);}
   pivot=new GameObject("Turntable");pivot.transform.SetParent(stage.transform,false);
   var mesh=CharacterCatalog.Mesh(module.mesh);var size=mesh.bounds.size;var axis=size.z>size.y&&size.z>size.x?Vector3.forward:size.x>size.y?Vector3.right:Vector3.up;orientation=Quaternion.FromToRotation(axis,Vector3.up);yaw=25;
   var model=new GameObject(module.id){layer=26};model.transform.SetParent(pivot.transform,false);model.transform.localPosition=-mesh.bounds.center;model.AddComponent<MeshFilter>().sharedMesh=mesh;model.AddComponent<MeshRenderer>().sharedMaterial=material;
   camera.orthographicSize=Mathf.Max(.05f,mesh.bounds.extents.magnitude)*1.12f;Tick();
  }
  public void Tick(){if(!camera||!camera.enabled||!pivot)return;yaw+=Time.unscaledDeltaTime*35;pivot.transform.localRotation=Quaternion.Euler(-10,yaw,-12)*orientation;}
  public void Hide(){if(camera)camera.enabled=false;}
  public void Dispose(){PreviewStudioLifetime.Release(stage,true);stage=null;texture=null;camera=null;pivot=null;material=null;}
 }
}
