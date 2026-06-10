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
        [SerializeField] private float jumpDelay = 0.2f;
        [SerializeField] private float groundedStickVelocity = -0.6f;
        [SerializeField] private LayerMask ledgeMask = ~0;
        [SerializeField] private float ledgeForwardCheckDistance = 0.34f;
        [SerializeField] private float ledgeForwardProbeHeight = 0.29f;
        [SerializeField] private float ledgeProbeRadius = 0.035f;
        [SerializeField] private float ledgeTopProbeHeight = 0.42f;
        [SerializeField] private float ledgeTopProbeDepth = 0.58f;
        [SerializeField] private float ledgeHangBackOffset = 0.08f;
        [SerializeField] private float ledgeHangDownOffset = 0.2f;
        [SerializeField] private float ledgeClimbForwardOffset = 0.16f;
        [SerializeField] private float ledgeStandHeightOffset = 0.16f;
        [SerializeField] private float ledgeSnapSpeed = 5f;
        [SerializeField] private Transform cameraPivot;

        private CharacterController characterController;
        private Vector3 verticalVelocity;
        private Vector3 lastMoveDirection = Vector3.forward;
        private float coyoteTimer;
        private float jumpBufferTimer;
        private float jumpDelayTimer;
        private bool jumpWindingUp;
        private bool ledgeHanging;
        private TerraMagePlayerMechanics.LedgeGrab activeLedgeGrab;

        public bool IsGrounded => characterController != null && characterController.isGrounded;
        public Transform CameraPivot => cameraPivot;
        public Vector3 LastMoveDirection => lastMoveDirection;
        public float JumpDelay => jumpDelay;
        public bool IsJumpWindingUp => jumpWindingUp;
        public bool IsLedgeHanging => ledgeHanging;

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
            if (UpdateLedgeHang())
            {
                return;
            }

            Vector2 moveInput = ReadMoveInput();
            Move(moveInput);
            JumpAndGravity(moveInput);
        }

        private void UpdateJumpInput()
        {
            jumpBufferTimer = TerraMagePlayerMechanics.UpdateJumpBuffer(
                jumpBufferTimer,
                TerraMageInput.GetKeyDown(KeyCode.Space),
                jumpBufferTime,
                Time.deltaTime);
        }

        private Vector2 ReadMoveInput()
        {
            float horizontal = TerraMageInput.GetAxisRaw("Horizontal");
            float vertical = TerraMageInput.GetAxisRaw("Vertical");
            return new Vector2(horizontal, vertical);
        }

        private void Move(Vector2 moveInput)
        {
            Vector3 move = TerraMagePlayerMechanics.BuildCameraRelativeMove(
                moveInput,
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

        private void JumpAndGravity(Vector2 moveInput)
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

            if (!jumpWindingUp && TerraMagePlayerMechanics.CanUseBufferedJump(jumpBufferTimer, coyoteTimer))
            {
                jumpWindingUp = true;
                jumpDelayTimer = Mathf.Max(0f, jumpDelay);
                jumpBufferTimer = 0f;
                coyoteTimer = 0f;
            }

            if (jumpWindingUp)
            {
                jumpDelayTimer = TerraMagePlayerMechanics.UpdateJumpDelayTimer(jumpDelayTimer, Time.deltaTime);
                if (jumpDelayTimer <= 0f)
                {
                    verticalVelocity.y = TerraMagePlayerMechanics.CalculateJumpVelocity(jumpHeight, gravity);
                    jumpWindingUp = false;
                }
            }
            else
            {
                verticalVelocity.y += gravity * Time.deltaTime;
            }

            characterController.Move(verticalVelocity * Time.deltaTime);
            TryStartLedgeHang(moveInput);
        }

        private bool UpdateLedgeHang()
        {
            if (!ledgeHanging)
            {
                return false;
            }

            Vector2 moveInput = ReadMoveInput();
            if (TerraMagePlayerMechanics.HasForwardParkourInput(moveInput.y))
            {
                CompleteLedgeClimb();
                return true;
            }

            if (TerraMagePlayerMechanics.HasBackwardParkourInput(moveInput.y))
            {
                ReleaseLedge();
                return false;
            }

            Vector3 nextPosition = TerraMagePlayerMechanics.MoveTowardLedgeAnchor(
                transform.position,
                activeLedgeGrab.HangPosition,
                ledgeSnapSpeed,
                Time.deltaTime);
            characterController.Move(nextPosition - transform.position);
            verticalVelocity = Vector3.zero;
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(activeLedgeGrab.FacingDirection, Vector3.up),
                16f * Time.deltaTime);
            return true;
        }

        private void TryStartLedgeHang(Vector2 moveInput)
        {
            if (ledgeHanging || characterController.isGrounded || jumpWindingUp)
            {
                return;
            }

            Vector3 preferredDirection = moveInput.sqrMagnitude > 0.001f
                ? TerraMagePlayerMechanics.BuildCameraRelativeMove(moveInput, cameraPivot, transform)
                : lastMoveDirection;
            if (!TerraMagePlayerMechanics.TryFindLedgeGrab(
                    transform,
                    preferredDirection,
                    ledgeForwardCheckDistance,
                    ledgeForwardProbeHeight,
                    ledgeProbeRadius,
                    ledgeTopProbeHeight,
                    ledgeTopProbeDepth,
                    ledgeHangBackOffset,
                    ledgeHangDownOffset,
                    ledgeClimbForwardOffset,
                    ledgeStandHeightOffset,
                    ledgeMask,
                    out TerraMagePlayerMechanics.LedgeGrab grab))
            {
                return;
            }

            activeLedgeGrab = grab;
            ledgeHanging = true;
            verticalVelocity = Vector3.zero;
            jumpBufferTimer = 0f;
            jumpWindingUp = false;
        }

        private void CompleteLedgeClimb()
        {
            characterController.enabled = false;
            transform.position = activeLedgeGrab.ClimbPosition;
            transform.rotation = Quaternion.LookRotation(activeLedgeGrab.FacingDirection, Vector3.up);
            characterController.enabled = true;
            verticalVelocity = Vector3.zero;
            ledgeHanging = false;
        }

        private void ReleaseLedge()
        {
            ledgeHanging = false;
            verticalVelocity = Vector3.down * Mathf.Abs(groundedStickVelocity);
        }
    }
}
