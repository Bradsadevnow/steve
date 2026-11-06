using System;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
namespace MoonTribe.UI
{
 // Real uGUI rendering for the comparison gallery and automated visual checks.
 public sealed class HealthbarCanvasPreview:IDisposable
 {
  public RenderTexture Texture {get;}
  public GameObject Instance {get;private set;}
  readonly GameObject host;
  readonly Canvas canvas;
  readonly Camera camera;
  public HealthbarCanvasPreview()
  {
   Texture=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32){name="Healthbar Canvas preview"};Texture.Create();
   host=new GameObject("Canvas preview renderer");
   camera=host.AddComponent<Camera>();camera.enabled=false;camera.targetTexture=Texture;camera.clearFlags=CameraClearFlags.SolidColor;
   camera.backgroundColor=new Color(.05f,.055f,.07f);camera.cullingMask=1<<31;camera.orthographic=true;camera.orthographicSize=450;
   var go=new GameObject("Canvas",typeof(RectTransform),typeof(Canvas));go.layer=31;go.transform.SetParent(host.transform,false);
   canvas=go.GetComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=10;
  }
  public void Show(GameObject prefab)
  {
   if(Instance){Instance.SetActive(false);UnityEngine.Object.Destroy(Instance);}
   Instance=UnityEngine.Object.Instantiate(prefab,canvas.transform,false);
   foreach(var t in Instance.GetComponentsInChildren<Transform>(true))t.gameObject.layer=31;
   var root=(RectTransform)Instance.transform;var size=root.rect.size;
   root.anchorMin=root.anchorMax=Vector2.one*.5f;root.anchoredPosition=Vector2.zero;root.localScale=Vector3.one;
   if(size.x<1||size.y<1)size=new Vector2(1920,1080);root.sizeDelta=size;
   Canvas.ForceUpdateCanvases();
   var min=new Vector2(float.MaxValue,float.MaxValue);var max=new Vector2(float.MinValue,float.MinValue);var corners=new Vector3[4];
   foreach(var image in Instance.GetComponentsInChildren<Graphic>(true))
   {
    if(!image.gameObject.activeInHierarchy)continue;
    image.rectTransform.GetWorldCorners(corners);
    foreach(var corner in corners){var p=(Vector2)root.InverseTransformPoint(corner);min=Vector2.Min(min,p);max=Vector2.Max(max,p);}
   }
   if(min.x==float.MaxValue){min=root.rect.min;max=root.rect.max;}
   var bounds=max-min;float scale=Mathf.Min(1,Mathf.Min(1540/Mathf.Max(1,bounds.x),840/Mathf.Max(1,bounds.y)));
   root.localScale=Vector3.one*scale;root.anchoredPosition=-(min+max)*.5f*scale;
   Canvas.ForceUpdateCanvases();
  }
  public void SetValue(float normalized,bool instant=true)
  {
   if(!Instance)return;
   foreach(var bar in Instance.GetComponentsInChildren<HealthBarUGUI>(true))
    if(instant)bar.SetValueInstant(normalized*bar.Model.Max);else bar.SetValue(normalized*bar.Model.Max);
  }
  public void Render(){Canvas.ForceUpdateCanvases();camera.Render();}
  public void Dispose()
  {
   host.SetActive(false);UnityEngine.Object.Destroy(host);Texture.Release();UnityEngine.Object.Destroy(Texture);
  }
 }
}

