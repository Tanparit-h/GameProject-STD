using UnityEngine;

namespace TerraMageTD
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class TerraMageTinyMageController : MonoBehaviour
    {
        [SerializeField] private float walkSpeed = 2.2f;
        [SerializeField] private float runSpeed = 4.2f;
        [SerializeField] private float jumpHeight = 0.55f;
        [SerializeField] private float gravity = -9.81f;
        [SerializeField] private float coyoteTime = 0.12f;
        [SerializeField] private float jumpBufferTime = 0.14f;
        [SerializeField] private float groundedStickVelocity = -0.6f;
        [SerializeField] private Transform cameraPivot;

        private CharacterController characterController;
        private Vector3 verticalVelocity;
        private Vector3 lastMoveDirection = Vector3.forward;
        private float coyoteTimer;
        private float jumpBufferTimer;

        public bool IsGrounded => characterController != null && characterController.isGrounded;
        public Transform CameraPivot => cameraPivot;
        public Vector3 LastMoveDirection => lastMoveDirection;

        private void Awake()
        {
            characterController = GetComponent<CharacterController>();
        }

        public void SetCameraPivot(Transform newPivot)
        {
            cameraPivot = newPivot;
        }

        private void Update()
        {
            UpdateJumpInput();
            Move();
            JumpAndGravity();
        }

        private void UpdateJumpInput()
        {
            if (TerraMageInput.GetKeyDown(KeyCode.Space))
            {
                jumpBufferTimer = jumpBufferTime;
                return;
            }

            jumpBufferTimer = Mathf.Max(0f, jumpBufferTimer - Time.deltaTime);
        }

        private void Move()
        {
            float horizontal = TerraMageInput.GetAxisRaw("Horizontal");
            float vertical = TerraMageInput.GetAxisRaw("Vertical");
            Vector3 input = new Vector3(horizontal, 0f, vertical);
            input = Vector3.ClampMagnitude(input, 1f);

            Transform basis = cameraPivot != null ? cameraPivot : transform;
            Vector3 forward = Vector3.ProjectOnPlane(basis.forward, Vector3.up).normalized;
            Vector3 right = Vector3.ProjectOnPlane(basis.right, Vector3.up).normalized;

            if (forward.sqrMagnitude < 0.001f)
            {
                forward = transform.forward;
            }

            if (right.sqrMagnitude < 0.001f)
            {
                right = transform.right;
            }

            Vector3 move = right * input.x + forward * input.z;
            bool running = TerraMageInput.GetKey(KeyCode.LeftShift) || TerraMageInput.GetKey(KeyCode.RightShift);
            float speed = running ? runSpeed : walkSpeed;
            characterController.Move(move * speed * Time.deltaTime);

            if (move.sqrMagnitude > 0.001f)
            {
                lastMoveDirection = move.normalized;
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    Quaternion.LookRotation(lastMoveDirection, Vector3.up),
                    12f * Time.deltaTime);
            }
        }

        private void JumpAndGravity()
        {
            if (characterController.isGrounded)
            {
                coyoteTimer = coyoteTime;
            }
            else
            {
                coyoteTimer = Mathf.Max(0f, coyoteTimer - Time.deltaTime);
            }

            if (characterController.isGrounded && verticalVelocity.y < 0f)
            {
                verticalVelocity.y = groundedStickVelocity;
            }

            if (jumpBufferTimer > 0f && coyoteTimer > 0f)
            {
                verticalVelocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
                jumpBufferTimer = 0f;
                coyoteTimer = 0f;
            }

            verticalVelocity.y += gravity * Time.deltaTime;
            characterController.Move(verticalVelocity * Time.deltaTime);
        }
    }
}
