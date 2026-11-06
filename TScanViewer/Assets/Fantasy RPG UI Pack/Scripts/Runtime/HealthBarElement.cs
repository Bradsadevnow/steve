using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    [UxmlElement]
    public partial class HealthBarElement : VisualElement
    {
        readonly HealthBarModel model = new HealthBarModel();
        readonly List<PaintedImage> layers = new List<PaintedImage>();
        IVisualElementScheduledItem animation;
        double previousTime;
        public HealthBarModel Model => model;
        public event Action<float> NormalizedChanged;
        public event Action Emptied { add => model.Emptied += value; remove => model.Emptied -= value; }
        public event Action Filled { add => model.Filled += value; remove => model.Filled -= value; }
        [UxmlAttribute] public float MaxValue { get => model.Max; set => model.SetMax(value); }
        [UxmlAttribute] public float Value { get => model.Current; set => model.SetCurrent(value); }
        [UxmlAttribute] public float SmoothSpeed { get; set; } = 4;
        public HealthBarElement()
        {
            model.Changed += Apply;
            RegisterCallback<AttachToPanelEvent>(_ =>
            {
                RefreshLayers();
                previousTime = Time.realtimeSinceStartupAsDouble;
                animation = schedule.Execute(() =>
                {
                    double now = Time.realtimeSinceStartupAsDouble;
                    model.SetSmoothSpeed(SmoothSpeed);
                    model.Tick((float)(now - previousTime)); previousTime = now;
                }).Every(16);
            });
            RegisterCallback<DetachFromPanelEvent>(_ => { animation?.Pause(); animation = null; });
        }
        public void RefreshLayers()
        {
            layers.Clear();
            this.Query<PaintedImage>().ForEach(image =>
            {
                var owner = image.GetFirstAncestorOfType<HealthBarElement>();
                if (owner == this) layers.Add(image);
            });
            Apply(model.Displayed);
        }
        public void SetValue(float value, bool instant = false) => model.SetCurrent(value, instant);
        public void SetMax(float value, bool keepRatio = false) => model.SetMax(value, keepRatio);
        public void Damage(float amount) => model.Change(-Mathf.Abs(amount));
        public void Heal(float amount) => model.Change(Mathf.Abs(amount));
        void Apply(float value)
        {
            foreach (var image in layers)
            {
                if (image.ResourceFill) image.Fill = value <= 0 || value >= 1 ? value : value * image.FillScale + image.FillOffset;
                if (image.ResourceEdge)
                {
                    image.style.visibility = value > 0 && value < 1 ? Visibility.Visible : Visibility.Hidden;
                    var position=new Vector2(image.EdgeOffsetX+value*image.EdgeTravelX,image.EdgeOffsetY+value*image.EdgeTravelY);
                    image.parent.style.translate = new Translate(position.x,position.y);
                    image.ClipTranslation=position; image.MarkDirtyRepaint();
                }
            }
            NormalizedChanged?.Invoke(value);
        }
    }
}
