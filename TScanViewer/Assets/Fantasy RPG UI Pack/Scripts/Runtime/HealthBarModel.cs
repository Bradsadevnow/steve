using System;
using UnityEngine;

namespace MoonTribe.UI
{
    /// <summary>Shared resource value. The owner calls Tick once per frame.</summary>
    public class HealthBarModel
    {
        public event Action<float> Changed;
        /// <summary>Logical value reached zero, before the visual animation finishes.</summary>
        public event Action Emptied;
        /// <summary>Logical value reached maximum, including changes to the maximum.</summary>
        public event Action Filled;
        float _max, _current, _displayed, _smoothSpeed;
        public float Max => _max;
        public float Current => _current;
        public float Target => Mathf.Clamp01(_current / _max);
        public float Displayed => _displayed;
        public bool IsAnimating => _displayed != Target;
        public HealthBarModel(float max = 100f, float smoothSpeed = 4f)
        {
            _max = ValidMax(max);
            SetSmoothSpeed(smoothSpeed);
            _current = _max;
            _displayed = 1;
        }
        static void RequireFinite(float value, string name)
        {
            if (float.IsNaN(value) || float.IsInfinity(value))
                throw new ArgumentOutOfRangeException(name, "Value must be finite.");
        }
        static float ValidMax(float value)
        {
            RequireFinite(value, nameof(value));
            return Mathf.Max(0.0001f, value);
        }
        public void SetMax(float max, bool keepRatio = false)
        {
            max = ValidMax(max);
            float previous = Target;
            float current = keepRatio ? previous * max : _current;
            _max = max;
            _current = Mathf.Clamp(current, 0, _max);
            if (_smoothSpeed <= 0) Snap();
            NotifyBoundary(previous);
        }
        public void SetCurrent(float value, bool instant = false)
        {
            RequireFinite(value, nameof(value));
            float previous = Target;
            _current = Mathf.Clamp(value, 0, _max);
            if (instant || _smoothSpeed <= 0) Snap();
            NotifyBoundary(previous);
        }
        void NotifyBoundary(float previous)
        {
            if (Target == 0 && previous > 0) Emptied?.Invoke();
            if (Target == 1 && previous < 1) Filled?.Invoke();
        }
        void Snap() { _displayed = Target; Changed?.Invoke(_displayed); }
        public void Change(float delta, bool instant = false) => SetCurrent(_current + delta, instant);
        public bool Tick(float deltaTime)
        {
            RequireFinite(deltaTime, nameof(deltaTime));
            if (!IsAnimating || deltaTime < 0) return IsAnimating;
            _displayed = _smoothSpeed <= 0 ? Target : Mathf.MoveTowards(_displayed, Target, _smoothSpeed * deltaTime);
            Changed?.Invoke(_displayed);
            return IsAnimating;
        }
        public void SetSmoothSpeed(float speed)
        {
            RequireFinite(speed, nameof(speed));
            _smoothSpeed = Mathf.Max(0, speed);
        }
    }
}
