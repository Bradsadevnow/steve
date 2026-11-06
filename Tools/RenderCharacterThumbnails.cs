// Unity CLI script eval_file statements. Re-run after changing module meshes.
var output=UnityEngine.Application.dataPath+"/Resources/Meadow/character/thumbnails";
System.IO.Directory.CreateDirectory(output);
var stage=new UnityEngine.GameObject("Module thumbnail bake"){hideFlags=UnityEngine.HideFlags.HideAndDontSave};stage.transform.position=new UnityEngine.Vector3(1400,-500,0);
var cameraObject=new UnityEngine.GameObject("Thumbnail camera");cameraObject.transform.SetParent(stage.transform,false);
var camera=cameraObject.AddComponent<UnityEngine.Camera>();camera.enabled=false;camera.orthographic=true;camera.aspect=1;camera.cullingMask=1<<27;camera.clearFlags=UnityEngine.CameraClearFlags.SolidColor;camera.backgroundColor=UnityEngine.Color.clear;camera.nearClipPlane=.01f;camera.farClipPlane=30;camera.allowHDR=false;
var cameraData=UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(camera);cameraData.renderPostProcessing=false;cameraData.renderShadows=false;
var lightObject=new UnityEngine.GameObject("Thumbnail light");lightObject.transform.SetParent(stage.transform,false);lightObject.transform.localRotation=UnityEngine.Quaternion.Euler(30,-30,0);var light=lightObject.AddComponent<UnityEngine.Light>();light.type=UnityEngine.LightType.Directional;light.intensity=1.2f;light.cullingMask=1<<27;
var material=new UnityEngine.Material(UnityEngine.Shader.Find("Steve/MeadowVertex"));
var target=new UnityEngine.RenderTexture(256,256,24,UnityEngine.RenderTextureFormat.ARGB32);target.Create();
var previous=UnityEngine.RenderTexture.active;int count=0;
try{
 foreach(var module in Steve.TScan.CharacterCatalog.Data.modules){
  var model=new UnityEngine.GameObject(module.id){layer=27};model.transform.SetParent(stage.transform,false);
  var mesh=Steve.TScan.CharacterCatalog.Mesh(module.mesh);var size=mesh.bounds.size;var longAxis=size.z>size.y&&size.z>size.x?UnityEngine.Vector3.forward:size.x>size.y?UnityEngine.Vector3.right:UnityEngine.Vector3.up;
  model.transform.localRotation=UnityEngine.Quaternion.Euler(-12,25,-18)*UnityEngine.Quaternion.FromToRotation(longAxis,UnityEngine.Vector3.up);
  model.AddComponent<UnityEngine.MeshFilter>().sharedMesh=mesh;var renderer=model.AddComponent<UnityEngine.MeshRenderer>();renderer.sharedMaterial=material;
  var bounds=renderer.bounds;camera.transform.position=bounds.center+UnityEngine.Vector3.back*8;camera.transform.rotation=UnityEngine.Quaternion.identity;camera.orthographicSize=UnityEngine.Mathf.Max(bounds.extents.x,bounds.extents.y)*1.18f;
  UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera,new UnityEngine.Rendering.Universal.UniversalRenderPipeline.SingleCameraRequest{destination=target});
  UnityEngine.RenderTexture.active=target;var pixels=new UnityEngine.Texture2D(256,256,UnityEngine.TextureFormat.RGBA32,false);pixels.ReadPixels(new UnityEngine.Rect(0,0,256,256),0,0);pixels.Apply();
  System.IO.File.WriteAllBytes(output+"/"+module.id+".png",UnityEngine.ImageConversion.EncodeToPNG(pixels));UnityEngine.Object.DestroyImmediate(pixels);UnityEngine.Object.DestroyImmediate(model);count++;
 }
}finally{UnityEngine.RenderTexture.active=previous;UnityEngine.Object.DestroyImmediate(stage);target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(material);}
UnityEditor.AssetDatabase.Refresh();
foreach(var module in Steve.TScan.CharacterCatalog.Data.modules){
 var path="Assets/Resources/Meadow/character/thumbnails/"+module.id+".png";var importer=(UnityEditor.TextureImporter)UnityEditor.AssetImporter.GetAtPath(path);importer.textureType=UnityEditor.TextureImporterType.Default;importer.alphaIsTransparency=true;importer.mipmapEnabled=false;importer.textureCompression=UnityEditor.TextureImporterCompression.Uncompressed;importer.SaveAndReimport();
}
UnityEngine.Debug.Log("Baked "+count+" module asset thumbnails from the current character meshes.");
