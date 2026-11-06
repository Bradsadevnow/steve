using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    /// <summary>Fits one authored composition uniformly within available space, without stretching its art.</summary>
    [UxmlElement]
    public partial class PaintedFrame : VisualElement
    {
        [UxmlAttribute] public float DesignWidth { get; set; } = 256;
        [UxmlAttribute] public float DesignHeight { get; set; } = 256;
        [UxmlAttribute] public float MaxScale { get; set; } = 1;
        public PaintedFrame()
        {
            style.overflow = Overflow.Hidden;
            RegisterCallback<GeometryChangedEvent>(_ => Fit());
            RegisterCallback<AttachToPanelEvent>(_ => schedule.Execute(Fit));
        }
        public void Fit()
        {
            if (childCount == 0 || DesignWidth <= 0 || DesignHeight <= 0) return;
            var child = this[0];
            float scale = Mathf.Min(contentRect.width / DesignWidth, contentRect.height / DesignHeight);
            if (MaxScale > 0) scale = Mathf.Min(scale, MaxScale);
            if (float.IsNaN(scale) || scale <= 0) return;
            child.style.position = Position.Absolute;
            child.style.width = DesignWidth; child.style.height = DesignHeight;
            child.style.transformOrigin = new TransformOrigin(0, 0);
            child.style.scale = new Scale(new Vector3(scale, scale, 1));
            child.style.left = (contentRect.width - DesignWidth * scale) * .5f;
            child.style.top = (contentRect.height - DesignHeight * scale) * .5f;
        }
    }
}
