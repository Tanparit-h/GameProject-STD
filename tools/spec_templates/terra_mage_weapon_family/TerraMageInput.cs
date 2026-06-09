using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace TerraMageTD
{
    public static class TerraMageInput
    {
        public static bool GetKey(KeyCode key)
        {
#if ENABLE_INPUT_SYSTEM
            Key mapped = ToInputSystemKey(key);
            return mapped != Key.None && Keyboard.current != null && Keyboard.current[mapped].isPressed;
#else
            return Input.GetKey(key);
#endif
        }

        public static bool GetKeyDown(KeyCode key)
        {
#if ENABLE_INPUT_SYSTEM
            Key mapped = ToInputSystemKey(key);
            return mapped != Key.None && Keyboard.current != null && Keyboard.current[mapped].wasPressedThisFrame;
#else
            return Input.GetKeyDown(key);
#endif
        }

        public static bool GetMouseButton(int button)
        {
#if ENABLE_INPUT_SYSTEM
            return GetMouseButtonControl(button)?.isPressed ?? false;
#else
            return Input.GetMouseButton(button);
#endif
        }

        public static bool GetMouseButtonDown(int button)
        {
#if ENABLE_INPUT_SYSTEM
            return GetMouseButtonControl(button)?.wasPressedThisFrame ?? false;
#else
            return Input.GetMouseButtonDown(button);
#endif
        }

        public static bool GetMouseButtonUp(int button)
        {
#if ENABLE_INPUT_SYSTEM
            return GetMouseButtonControl(button)?.wasReleasedThisFrame ?? false;
#else
            return Input.GetMouseButtonUp(button);
#endif
        }

        public static Vector2 MousePosition()
        {
#if ENABLE_INPUT_SYSTEM
            return Mouse.current != null ? Mouse.current.position.ReadValue() : Vector2.zero;
#else
            return Input.mousePosition;
#endif
        }

        public static Vector2 MouseDelta()
        {
#if ENABLE_INPUT_SYSTEM
            return Mouse.current != null ? Mouse.current.delta.ReadValue() : Vector2.zero;
#else
            return new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y"));
#endif
        }

        public static float GetAxisRaw(string axisName)
        {
#if ENABLE_INPUT_SYSTEM
            if (axisName == "Horizontal")
            {
                return DigitalAxis(Key.A, Key.D, Key.LeftArrow, Key.RightArrow);
            }

            if (axisName == "Vertical")
            {
                return DigitalAxis(Key.S, Key.W, Key.DownArrow, Key.UpArrow);
            }

            if (axisName == "Mouse X")
            {
                return Mouse.current != null ? Mouse.current.delta.ReadValue().x : 0f;
            }

            if (axisName == "Mouse Y")
            {
                return Mouse.current != null ? Mouse.current.delta.ReadValue().y : 0f;
            }

            return 0f;
#else
            return Input.GetAxisRaw(axisName);
#endif
        }

#if ENABLE_INPUT_SYSTEM
        private static float DigitalAxis(Key negative, Key positive, Key altNegative, Key altPositive)
        {
            if (Keyboard.current == null)
            {
                return 0f;
            }

            float value = 0f;
            if (Keyboard.current[negative].isPressed || Keyboard.current[altNegative].isPressed)
            {
                value -= 1f;
            }

            if (Keyboard.current[positive].isPressed || Keyboard.current[altPositive].isPressed)
            {
                value += 1f;
            }

            return Mathf.Clamp(value, -1f, 1f);
        }

        private static UnityEngine.InputSystem.Controls.ButtonControl GetMouseButtonControl(int button)
        {
            if (Mouse.current == null)
            {
                return null;
            }

            return button switch
            {
                0 => Mouse.current.leftButton,
                1 => Mouse.current.rightButton,
                2 => Mouse.current.middleButton,
                _ => null,
            };
        }

        private static Key ToInputSystemKey(KeyCode key)
        {
            return key switch
            {
                KeyCode.Tab => Key.Tab,
                KeyCode.Q => Key.Q,
                KeyCode.E => Key.E,
                KeyCode.R => Key.R,
                KeyCode.Space => Key.Space,
                KeyCode.LeftShift => Key.LeftShift,
                KeyCode.RightShift => Key.RightShift,
                KeyCode.Alpha1 => Key.Digit1,
                KeyCode.Alpha2 => Key.Digit2,
                KeyCode.Alpha3 => Key.Digit3,
                KeyCode.Alpha4 => Key.Digit4,
                _ => Key.None,
            };
        }
#endif
    }
}
