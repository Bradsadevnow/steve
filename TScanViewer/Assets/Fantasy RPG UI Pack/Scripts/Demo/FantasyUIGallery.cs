using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    [RequireComponent(typeof(UIDocument))]
    public class FantasyUIGallery : MonoBehaviour
    {
        [SerializeField] FantasyUICatalog catalog;
        VisualElement stage;
        ScrollView browser;
        Label title, feedback;
        readonly Dictionary<string,bool> expanded = new Dictionary<string,bool>();
        float resource=65, maxScale=1;
        string query="";
        Button selected;
        static readonly Color Ink=new Color(.87f,.88f,.9f);
        void OnEnable()
        {
            var root=GetComponent<UIDocument>().rootVisualElement; root.Clear();
            root.style.flexDirection=FlexDirection.Row; root.style.flexGrow=1;
            root.style.backgroundColor=new Color(.045f,.052f,.067f); root.style.color=Ink;
            var sidebar=new VisualElement(); sidebar.style.width=340; sidebar.style.flexShrink=0;
            sidebar.style.paddingTop=18; sidebar.style.paddingLeft=12; sidebar.style.paddingRight=12;
            var heading=new Label("MOON TRIBE / FANTASY UI"); heading.style.color=new Color(.88f,.72f,.42f); heading.style.fontSize=18; sidebar.Add(heading);
            var search=new TextField("Search"); sidebar.Add(search);
            browser=new ScrollView(ScrollViewMode.Vertical); browser.style.flexGrow=1; sidebar.Add(browser); root.Add(sidebar);
            var main=new VisualElement(); main.style.flexGrow=1; main.style.minWidth=0; main.style.paddingLeft=20; main.style.paddingRight=20; main.style.paddingTop=18; main.style.paddingBottom=18;
            title=new Label(); title.style.fontSize=22; title.style.color=Color.white; main.Add(title);
            var preview=new DropdownField("Preview scale",new List<string>{"Natural size (up to 100%)","Up to 200%","Fit available area"},0);
            preview.RegisterValueChangedCallback(e=>{ maxScale=e.newValue.StartsWith("Natural")?1:e.newValue.StartsWith("Up")?2:0; ApplyScale(); }); main.Add(preview);
            stage=new VisualElement(); stage.style.flexGrow=1; stage.style.minHeight=0; stage.style.marginTop=20; stage.style.marginBottom=16; main.Add(stage);
            feedback=new Label("Select an item from a folder."); feedback.style.color=Ink; main.Add(feedback);
            var slider=new Slider("Resource %",0,100){value=resource}; slider.style.marginTop=12;
            slider.RegisterValueChangedCallback(e=>{resource=e.newValue;SetResources();}); main.Add(slider); root.Add(main);
            root.Query<Label>().ForEach(l=>l.style.color=Ink); heading.style.color=new Color(.88f,.72f,.42f);
            foreach(var input in new[]{search.Q(className:"unity-base-field__input"),preview.Q(className:"unity-base-field__input")})
                if(input!=null) { input.style.backgroundColor=new Color(.09f,.11f,.14f); input.style.color=Ink; }
            search.RegisterValueChangedCallback(e=>{query=e.newValue??"";RebuildBrowser();});
            RebuildBrowser();
            if(catalog && catalog.entries.Length>0) Show(catalog.entries[0]);
        }
        static string SortKey(string text)=>Regex.Replace(text,@"\d+",m=>m.Value.PadLeft(8,'0'));
        void RebuildBrowser()
        {
            browser.Clear(); selected=null;
            if(!catalog) return;
            var entries=catalog.entries.Where(e=>e.id.IndexOf(query,StringComparison.OrdinalIgnoreCase)>=0).OrderBy(e=>SortKey(e.id)).ToArray();
            if(entries.Length==0) {browser.Add(new Label("No matches")); return;}
            AddBranch(browser,entries,"",0);
        }
        void AddBranch(VisualElement parent,FantasyUICatalog.Entry[] entries,string prefix,int depth)
        {
            foreach(var group in entries.GroupBy(e=>e.id.Substring(prefix.Length).Split('/')[0]))
            {
                string path=prefix+group.Key;
                var leaf=group.FirstOrDefault(e=>e.id==path);
                if(leaf!=null)
                {
                    var button=new Button(()=>Show(leaf)){text=group.Key,tooltip=leaf.id};
                    button.style.unityTextAlign=TextAnchor.MiddleLeft; button.style.color=Ink;
                    button.style.backgroundColor=new Color(.09f,.11f,.14f); button.style.height=28; button.style.marginLeft=0;
                    button.clicked+=()=>{if(selected!=null) selected.style.backgroundColor=new Color(.09f,.11f,.14f);selected=button;button.style.backgroundColor=new Color(.25f,.29f,.35f);};
                    parent.Add(button);
                }
                else
                {
                    bool open=query.Length>0 || (expanded.TryGetValue(path,out bool stored)?stored:depth==0 && group.Key=="Boards");
                    var folder=new Foldout{text=group.Key.Replace('_',' ')+" ("+group.Count()+")",value=open};
                    folder.RegisterValueChangedCallback(e=>{if(e.target==folder && query.Length==0)expanded[path]=e.newValue;});
                    parent.Add(folder); AddBranch(folder,group.ToArray(),path+"/",depth+1);
                    folder.Query<Label>().ForEach(l=>l.style.color=Ink);
                }
            }
        }
        void Show(FantasyUICatalog.Entry entry)
        {
            stage.Clear();title.text=entry.id;
            if(!entry.template){feedback.text="Missing template";return;}
            var tree=entry.template.Instantiate();tree.style.flexGrow=1;tree.style.minHeight=0;stage.Add(tree);
            feedback.text="Painted proportions preserved. Preview scale does not alter the asset.";
            tree.Query<Button>().ForEach(b=>b.clicked+=()=>feedback.text="Clicked: "+b.name);
            tree.schedule.Execute(()=>{ApplyScale();SetResources();});
        }
        void ApplyScale()=>stage.Query<PaintedFrame>().ForEach(f=>{f.MaxScale=maxScale;f.Fit();});
        void SetResources()=>stage.Query<HealthBarElement>().ForEach(b=>b.SetValue(resource*.01f*b.Model.Max));
    }
}

