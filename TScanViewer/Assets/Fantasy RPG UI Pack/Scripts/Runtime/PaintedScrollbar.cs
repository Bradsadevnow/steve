using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    /// <summary>Interactive scrollbar retaining the authored track and thumb artwork.</summary>
    [UxmlElement]
    public partial class PaintedScrollbar : VisualElement, INotifyValueChanged<float>
    {
        float current, grabOffset;
        int pointer = -1;
        VisualElement track, thumb;
        [UxmlAttribute] public string TrackName { get; set; } = "Sliding Area";
        [UxmlAttribute] public string ThumbName { get; set; } = "Handle";
        [UxmlAttribute] public bool Horizontal { get; set; }
        [UxmlAttribute] public bool Reversed { get; set; }
        [UxmlAttribute] public float Step { get; set; } = .05f;
        // Authored distance between the starting positions of the thumb at both ends.
        [UxmlAttribute] public float TravelLength { get; set; } = -1;
        [UxmlAttribute] public float value
        {
            get => current;
            set
            {
                float next = float.IsNaN(value) ? 0 : Mathf.Clamp01(value);
                if (Mathf.Approximately(next,current)) return;
                using (var evt = ChangeEvent<float>.GetPooled(current,next))
                { evt.target=this; SetValueWithoutNotify(next); SendEvent(evt); }
            }
        }
        public PaintedScrollbar()
        {
            focusable=true; tabIndex=0;
            RegisterCallback<AttachToPanelEvent>(_ => schedule.Execute(Refresh));
            RegisterCallback<GeometryChangedEvent>(_ => Refresh());
            RegisterCallback<PointerDownEvent>(e =>
            {
                if (e.button != 0 || !enabledInHierarchy) return;
                Refresh(); if(track==null || thumb==null) return;
                Focus(); pointer=e.pointerId;
                var local = thumb.WorldToLocal(e.position);
                grabOffset=thumb.worldBound.Contains(e.position) ? (Horizontal?local.x:local.y) : ThumbSize*.5f;
                this.CapturePointer(pointer); Move(e.position); e.StopPropagation();
            });
            RegisterCallback<PointerMoveEvent>(e => { if(e.pointerId==pointer && this.HasPointerCapture(pointer)) { Move(e.position); e.StopPropagation(); } });
            RegisterCallback<PointerUpEvent>(e => { if(e.pointerId==pointer) { this.ReleasePointer(pointer); pointer=-1; e.StopPropagation(); } });
            RegisterCallback<PointerCaptureOutEvent>(_ => pointer=-1);
            RegisterCallback<KeyDownEvent>(e =>
            {
                float direction=0;
                if(e.keyCode==KeyCode.Home) value=0;
                else if(e.keyCode==KeyCode.End) value=1;
                else if(e.keyCode==KeyCode.LeftArrow || e.keyCode==KeyCode.UpArrow) direction=-1;
                else if(e.keyCode==KeyCode.RightArrow || e.keyCode==KeyCode.DownArrow) direction=1;
                else return;
                if(direction!=0) value+=direction*(Reversed?-1:1)*Step;
                e.StopPropagation();
            });
        }
        float ThumbSize => Horizontal?thumb.layout.width:thumb.layout.height;
        public float Travel => TravelLength >= 0 ? TravelLength : Mathf.Max(0,(Horizontal?track.contentRect.width:track.contentRect.height)-ThumbSize);
        public void SetValueWithoutNotify(float next) { current=float.IsNaN(next)?0:Mathf.Clamp01(next); PositionThumb(); }
        public void Refresh() { track=this.Q(TrackName); thumb=this.Q(ThumbName); PositionThumb(); }
        void PositionThumb()
        {
            if(track==null || thumb==null) return;
            float position=(Reversed?1-current:current)*Travel;
            if(Horizontal) thumb.style.left=position; else thumb.style.top=position;
        }
        void Move(Vector2 point)
        {
            if(Travel<=0) return;
            var local=track.WorldToLocal(point);
            float fraction=((Horizontal?local.x:local.y)-grabOffset)/Travel;
            value=Reversed?1-fraction:fraction;
        }
    }
}
