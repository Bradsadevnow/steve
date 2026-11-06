using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    /// <summary>Draws painted sprites at their original proportions. Fill clips UVs; never uses slicing.</summary>
    [UxmlElement]
    public partial class PaintedImage : VisualElement
    {
        Sprite _sprite;
        Color _tint = Color.white;
        float _fill = 1;
        [UxmlAttribute] public Sprite Sprite { get => _sprite; set { _sprite = value; MarkDirtyRepaint(); } }
        [UxmlAttribute] public Color Tint { get => _tint; set { _tint = value; MarkDirtyRepaint(); } }
        [UxmlAttribute] public float Fill { get => _fill; set { _fill = Mathf.Clamp01(value); MarkDirtyRepaint(); } }
        [UxmlAttribute] public bool Vertical { get; set; }
        [UxmlAttribute] public bool Reverse { get; set; }
        [UxmlAttribute] public bool PreserveAspect { get; set; }
        [UxmlAttribute] public bool ResourceFill { get; set; }
        [UxmlAttribute] public float FillScale { get; set; } = 1;
        [UxmlAttribute] public float FillOffset { get; set; }
        [UxmlAttribute] public bool ResourceEdge { get; set; }
        Material _effectMaterial;
        MaterialDefinition _effectDefinition;
        IVisualElementScheduledItem _effectClock;
        [UxmlAttribute] public Material EffectMaterial
        {
            get => _effectMaterial;
            set
            {
                _effectMaterial = value;
                if(value) _effectDefinition = new MaterialDefinition(value);
                style.unityMaterial = value ? new StyleMaterialDefinition(_effectDefinition) : new StyleMaterialDefinition(StyleKeyword.Null);
                BindEffectClock(); MarkDirtyRepaint();
            }
        }
        [UxmlAttribute] public float EdgeTravelX { get; set; }
        [UxmlAttribute] public float EdgeTravelY { get; set; }
        [UxmlAttribute] public float EdgeOffsetX { get; set; }
        [UxmlAttribute] public float EdgeOffsetY { get; set; }
        [UxmlAttribute] public PaintedClipShape ClipShape { get; set; }
        [UxmlAttribute] public float ClipX { get; set; }
        [UxmlAttribute] public float ClipY { get; set; }
        [UxmlAttribute] public float ClipWidth { get; set; }
        [UxmlAttribute] public float ClipHeight { get; set; }
        public Vector2 ClipTranslation { get; set; }
        public PaintedImage()
        {
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            RegisterCallback<AttachToPanelEvent>(_=>BindEffectClock());
            RegisterCallback<DetachFromPanelEvent>(_=>{_effectClock?.Pause();_effectClock=null;});
        }
        void BindEffectClock()
        {
            _effectClock?.Pause();_effectClock=null;
            if(panel!=null && _effectMaterial && _effectMaterial.HasProperty("_MoonTime"))
            {
                UpdateEffectClock();_effectClock=schedule.Execute(UpdateEffectClock).Every(16);
            }
        }
        void UpdateEffectClock()
        {
            _effectDefinition.SetFloat("_MoonTime",Application.isPlaying?Time.time:Time.realtimeSinceStartup);
            style.unityMaterial=new StyleMaterialDefinition(_effectDefinition);
            MarkDirtyRepaint();
        }
        void Draw(MeshGenerationContext context)
        {
            if (!_sprite || _fill <= 0 || contentRect.width <= 0 || contentRect.height <= 0) return;
            Rect r = contentRect;
            if (PreserveAspect)
            {
                float scale = Mathf.Min(r.width / _sprite.rect.width, r.height / _sprite.rect.height);
                var size = _sprite.rect.size * scale;
                r = new Rect(r.center - size * 0.5f, size);
            }
            var texture = _sprite.texture;
            // Standalone sprites: keep the full authored rectangle, including transparent padding.
            Rect tex = _sprite.rect;
            float u0 = tex.xMin / texture.width, u1 = tex.xMax / texture.width;
            float v0 = tex.yMin / texture.height, v1 = tex.yMax / texture.height;
            if (Vertical)
            {
                if (Reverse) { r.height *= _fill; v0 = Mathf.Lerp(v1, v0, _fill); }
                else { float h = r.height; r.y += h * (1 - _fill); r.height = h * _fill; v1 = Mathf.Lerp(v0, v1, _fill); }
            }
            else
            {
                if (Reverse) { float w = r.width; r.x += w * (1 - _fill); r.width = w * _fill; u0 = Mathf.Lerp(u1, u0, _fill); }
                else { r.width *= _fill; u1 = Mathf.Lerp(u0, u1, _fill); }
            }
            if(ClipShape && ClipWidth>0 && ClipHeight>0)
            {
                DrawClipped(context,r,texture,u0,u1,v0,v1); return;
            }
            var mesh = context.Allocate(4, 6, texture);
            mesh.SetNextVertex(V(r.xMin, r.yMin, u0, v1));
            mesh.SetNextVertex(V(r.xMax, r.yMin, u1, v1));
            mesh.SetNextVertex(V(r.xMax, r.yMax, u1, v0));
            mesh.SetNextVertex(V(r.xMin, r.yMax, u0, v0));
            mesh.SetNextIndex(0); mesh.SetNextIndex(1); mesh.SetNextIndex(2);
            mesh.SetNextIndex(2); mesh.SetNextIndex(3); mesh.SetNextIndex(0);
        }
        Vertex V(float x, float y, float u, float v) => new Vertex
        {
            position = new Vector3(x, y, Vertex.nearZ), tint = _tint,
            uv = new Vector2(u, v)
        };
        void DrawClipped(MeshGenerationContext context,Rect r,Texture texture,float u0,float u1,float v0,float v1)
        {
            var vertices=new System.Collections.Generic.List<Vertex>();
            float left=ClipX-ClipTranslation.x, top=ClipY-ClipTranslation.y;
            int count=ClipShape.spans.Length-1;
            for(int i=0;i<count;i++)
            {
                float y0=Mathf.Max(r.yMin,top+ClipHeight*i/count), y1=Mathf.Min(r.yMax,top+ClipHeight*(i+1)/count);
                if(y1<=y0) continue;
                var a=ClipShape.At((y0-top)/ClipHeight); var b=ClipShape.At((y1-top)/ClipHeight);
                float l0=Mathf.Max(r.xMin,left+a.x*ClipWidth), h0=Mathf.Min(r.xMax,left+a.y*ClipWidth);
                float l1=Mathf.Max(r.xMin,left+b.x*ClipWidth), h1=Mathf.Min(r.xMax,left+b.y*ClipWidth);
                if(l0>=h0 || l1>=h1) continue;
                vertices.Add(V(l0,y0,Mathf.Lerp(u0,u1,(l0-r.x)/r.width),Mathf.Lerp(v1,v0,(y0-r.y)/r.height)));
                vertices.Add(V(h0,y0,Mathf.Lerp(u0,u1,(h0-r.x)/r.width),Mathf.Lerp(v1,v0,(y0-r.y)/r.height)));
                vertices.Add(V(h1,y1,Mathf.Lerp(u0,u1,(h1-r.x)/r.width),Mathf.Lerp(v1,v0,(y1-r.y)/r.height)));
                vertices.Add(V(l1,y1,Mathf.Lerp(u0,u1,(l1-r.x)/r.width),Mathf.Lerp(v1,v0,(y1-r.y)/r.height)));
            }
            if(vertices.Count==0) return;
            var mesh=context.Allocate(vertices.Count,vertices.Count/4*6,texture);
            foreach(var vertex in vertices) mesh.SetNextVertex(vertex);
            for(ushort i=0;i<vertices.Count;i+=4) {mesh.SetNextIndex(i);mesh.SetNextIndex((ushort)(i+1));mesh.SetNextIndex((ushort)(i+2));mesh.SetNextIndex((ushort)(i+2));mesh.SetNextIndex((ushort)(i+3));mesh.SetNextIndex(i);}
        }
    }
}

