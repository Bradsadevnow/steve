using System.Collections.Generic;
using UnityEngine;

namespace Steve.TScan {
 // Player-facing decoration only: local +Z is north and local +X is east.
 [DefaultExecutionOrder(250)]
 public sealed class GridCompassVisuals:MonoBehaviour {
  readonly List<Transform> labels=new List<Transform>();
  Material textMaterial,plateMaterial;
  Font font;
  Camera eye;
  public int LabelCount=>labels.Count;
  void Awake(){
   font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
   font.RequestCharactersInTexture("NORTHSOUTH EASTWEST",64,FontStyle.Bold);
   textMaterial=new Material(Shader.Find("Steve/Depth Tested Label"));textMaterial.mainTexture=font.material.mainTexture;
   Font.textureRebuilt+=RefreshFont;
   plateMaterial=new Material(Shader.Find("Universal Render Pipeline/Unlit"));plateMaterial.SetColor("_BaseColor",new Color(.025f,.065f,.075f));
   AddLabel("NORTH",new Vector3(0,.95f,16.0f));
   AddLabel("SOUTH",new Vector3(0,.95f,-16.0f));
   AddLabel("EAST",new Vector3(16.0f,.95f,0));
   AddLabel("WEST",new Vector3(-16.0f,.95f,0));
  }
  void AddLabel(string direction,Vector3 position){
   var root=new GameObject("Compass / "+direction);root.layer=30;root.transform.SetParent(transform,false);root.transform.localPosition=position;labels.Add(root.transform);
   var plate=GameObject.CreatePrimitive(PrimitiveType.Quad);plate.name="Compass sign backing";plate.layer=30;plate.transform.SetParent(root.transform,false);plate.transform.localPosition=Vector3.forward*.015f;plate.transform.localScale=new Vector3(1.55f,.52f,1);
   var collider=plate.GetComponent<Collider>();collider.enabled=false;Destroy(collider);plate.GetComponent<Renderer>().sharedMaterial=plateMaterial;
   var lettering=new GameObject("Compass text",typeof(TextMesh));lettering.layer=30;lettering.transform.SetParent(root.transform,false);
   var text=lettering.GetComponent<TextMesh>();text.font=font;text.text=direction;text.fontSize=64;text.fontStyle=FontStyle.Bold;text.characterSize=.055f;text.anchor=TextAnchor.MiddleCenter;text.alignment=TextAlignment.Center;text.color=new Color(.75f,.94f,.95f);
   lettering.GetComponent<MeshRenderer>().sharedMaterial=textMaterial;
  }
  void RefreshFont(Font changed){if(changed==font&&textMaterial)textMaterial.mainTexture=font.material.mainTexture;}
  void LateUpdate(){
   if(!eye)eye=FindAnyObjectByType<SteveBody>()?.BodyCamera;
   if(!eye)return;
   foreach(var label in labels)label.rotation=eye.transform.rotation;
  }
  void OnDestroy(){Font.textureRebuilt-=RefreshFont;if(textMaterial)Destroy(textMaterial);if(plateMaterial)Destroy(plateMaterial);}
 }
}
