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
            jumpBufferTimer = TerraMagePlayerMechanics.UpdateJumpBuffer(
                jumpBufferTimer,
                TerraMageInput.GetKeyDown(KeyCode.Space),
                jumpBufferTime,
                Time.deltaTime);
        }

        private void Move()
        {
            float horizontal = TerraMageInput.GetAxisRaw("Horizontal");
            float vertical = TerraMageInput.GetAxisRaw("Vertical");
            Vector3 move = TerraMagePlayerMechanics.BuildCameraRelativeMove(
                new Vector2(horizontal, vertical),
                cameraPivot,
                transform);
            bool running = TerraMageInput.GetKey(KeyCode.LeftShift) || TerraMageInput.GetKey(KeyCode.RightShift);
            float speed = TerraMagePlayerMechanics.ResolveMoveSpeed(running, walkSpeed, runSpeed);
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
            coyoteTimer = TerraMagePlayerMechanics.UpdateCoyoteTimer(
                coyoteTimer,
                characterController.isGrounded,
                coyoteTime,
                Time.deltaTime);

            if (characterController.isGrounded && verticalVelocity.y < 0f)
            {
                verticalVelocity.y = groundedStickVelocity;
            }

            if (TerraMagePlayerMechanics.CanUseBufferedJump(jumpBufferTimer, coyoteTimer))
            {
                verticalVelocity.y = TerraMagePlayerMechanics.CalculateJumpVelocity(jumpHeight, gravity);
                jumpBufferTimer = 0f;
                coyoteTimer = 0f;
            }

            verticalVelocity.y += gravity * Time.deltaTime;
            characterController.Move(verticalVelocity * Time.deltaTime);
        }
    }
}
