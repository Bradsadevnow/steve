using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoonTribe.UI
{
 [RequireComponent(typeof(UIDocument))]
 public class HealthbarComparison:MonoBehaviour
 {
  public HealthbarVariantCatalog catalog;
  public VisualElement Stage {get;private set;}
  public HealthbarCanvasPreview CanvasPreview {get;private set;}
  public bool UseCanvas {get;private set;}
  public bool UseShader {get;private set;}
  public int Selected {get;private set;}
  float resource=.65f;
  DropdownField choice,system,variant;
  Slider slider;
  void OnEnable()
  {
   var root=GetComponent<UIDocument>().rootVisualElement;root.Clear();root.style.flexGrow=1;root.style.backgroundColor=new Color(.05f,.055f,.07f);root.style.color=Color.white;
   root.style.paddingLeft=root.style.paddingRight=18;root.style.paddingTop=root.style.paddingBottom=12;
   var title=new Label("MOON TRIBE / HEALTHBAR COMPARISON");title.style.fontSize=22;root.Add(title);
   choice=new DropdownField("Healthbar",catalog.entries.Select(e=>e.id).ToList(),0);root.Add(choice);
   system=new DropdownField("UI system",new System.Collections.Generic.List<string>{"Canvas (uGUI)","UI Toolkit"},0);root.Add(system);
   variant=new DropdownField("Presentation",new System.Collections.Generic.List<string>{"Painted / no custom shader","Animated / Shader Graph"},0);root.Add(variant);
   Stage=new VisualElement();Stage.style.flexGrow=1;Stage.style.minHeight=0;root.Add(Stage);
   slider=new Slider("Resource %",0,100){value=65};root.Add(slider);
   var actions=new VisualElement();actions.style.flexDirection=FlexDirection.Row;root.Add(actions);
   actions.Add(new Button(()=>SetValue(0,false)){text="Empty"});actions.Add(new Button(()=>SetValue(1,false)){text="Full"});
   actions.Add(new Button(()=>SetValue(Mathf.Clamp01(resource-.1f),false)){text="Damage 10%"});actions.Add(new Button(()=>SetValue(Mathf.Clamp01(resource+.1f),false)){text="Heal 10%"});
   slider.RegisterValueChangedCallback(e=>SetValue(e.newValue/100,false));
   choice.RegisterValueChangedCallback(_=>Show(choice.index,system.index==0,variant.index==1));
   system.RegisterValueChangedCallback(_=>Show(choice.index,system.index==0,variant.index==1));
   variant.RegisterValueChangedCallback(_=>Show(choice.index,system.index==0,variant.index==1));
   root.Query<Label>().ForEach(l=>l.style.color=new Color(.88f,.89f,.91f));
   foreach(var field in new[]{choice,system,variant}) {var input=field.Q(className:"unity-base-field__input");input.style.backgroundColor=new Color(.09f,.11f,.14f);}
   actions.Query<Button>().ForEach(b=>{b.style.backgroundColor=new Color(.12f,.15f,.19f);b.style.color=Color.white;});
   Show(0,true,false);
  }
  public void Show(int index,bool canvas,bool shader)
  {
   choice.SetValueWithoutNotify(catalog.entries[index].id);system.SetValueWithoutNotify(canvas?"Canvas (uGUI)":"UI Toolkit");variant.SetValueWithoutNotify(shader?"Animated / Shader Graph":"Painted / no custom shader");
   Selected=index;UseCanvas=canvas;UseShader=shader;Stage.Clear();CanvasPreview?.Dispose();CanvasPreview=null;
   var entry=catalog.entries[index];
   if(canvas)
   {
    CanvasPreview=new HealthbarCanvasPreview();CanvasPreview.Show(shader?entry.canvasShader:entry.canvasPlain);
    var image=new Image {image=CanvasPreview.Texture,scaleMode=ScaleMode.ScaleToFit};image.style.flexGrow=1;image.style.minHeight=0;Stage.Add(image);
   }
   else {var tree=(shader?entry.toolkitShader:entry.toolkitPlain).Instantiate();tree.style.flexGrow=1;tree.style.minHeight=0;Stage.Add(tree);}
   Stage.schedule.Execute(()=>SetValue(resource,true));
  }
  public void SetValue(float normalized,bool instant=true)
  {
   resource=Mathf.Clamp01(normalized);slider.SetValueWithoutNotify(resource*100);
   if(UseCanvas)CanvasPreview?.SetValue(resource,instant);
   else Stage.Query<HealthBarElement>().ForEach(b=>b.SetValue(resource*b.Model.Max,instant));
  }
  void LateUpdate(){CanvasPreview?.Render();}
  void OnDisable(){CanvasPreview?.Dispose();CanvasPreview=null;}
 }
}

