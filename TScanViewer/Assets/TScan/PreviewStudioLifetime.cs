using System.Collections.Generic;
using UnityEngine;

namespace Steve.TScan {
 // Releases only a named cosmetic studio's owned targets/materials, never catalog meshes.
 public static class PreviewStudioLifetime {
  public static void Reclaim(Transform owner,string name,bool ownsMaterials=false){
   // FindObjectsByType omits DontSave roots. Traverse this owner's hierarchy instead.
   foreach(var candidate in owner.GetComponentsInChildren<Transform>(true))if(candidate.name==name)Release(candidate.gameObject,ownsMaterials);
   // Recover root-level studios created by older builds before they were parented to the viewer.
   foreach(var candidate in Resources.FindObjectsOfTypeAll<Transform>())
    if(candidate.name==name&&candidate.parent==null&&candidate.gameObject.scene.IsValid()&&(candidate.gameObject.hideFlags&HideFlags.DontSave)!=0)Release(candidate.gameObject,ownsMaterials);
  }
  public static void Release(GameObject studio,bool ownsMaterials=false){
   if(!studio)return;studio.SetActive(false);
   var textures=new HashSet<RenderTexture>();
   foreach(var camera in studio.GetComponentsInChildren<Camera>(true)){
    camera.enabled=false;if(camera.targetTexture)textures.Add(camera.targetTexture);camera.targetTexture=null;
   }
   foreach(var texture in textures){texture.Release();Object.Destroy(texture);}
   if(ownsMaterials){
    var materials=new HashSet<Material>();foreach(var renderer in studio.GetComponentsInChildren<Renderer>(true))foreach(var material in renderer.sharedMaterials)if(material)materials.Add(material);
    foreach(var material in materials)Object.Destroy(material);
   }
   Object.Destroy(studio);
  }
 }
}
