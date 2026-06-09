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
        [SerializeField] private Transform cameraPivot;

        private CharacterController characterController;
        private Vector3 verticalVelocity;

        public bool IsGrounded => characterController != null && characterController.isGrounded;

        private void Awake()
        {
            characterController = GetComponent<CharacterController>();
        }

        private void Update()
        {
            Move();
            JumpAndGravity();
        }

        private void Move()
        {
            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");
            Vector3 input = new Vector3(horizontal, 0f, vertical);
            input = Vector3.ClampMagnitude(input, 1f);

            Transform basis = cameraPivot != null ? cameraPivot : transform;
            Vector3 forward = Vector3.ProjectOnPlane(basis.forward, Vector3.up).normalized;
            Vector3 right = Vector3.ProjectOnPlane(basis.right, Vector3.up).normalized;
            Vector3 move = right * input.x + forward * input.z;

            bool running = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
            float speed = running ? runSpeed : walkSpeed;
            characterController.Move(move * speed * Time.deltaTime);

            if (move.sqrMagnitude > 0.001f)
            {
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    Quaternion.LookRotation(move, Vector3.up),
                    12f * Time.deltaTime);
            }
        }

        private void JumpAndGravity()
        {
            if (characterController.isGrounded && verticalVelocity.y < 0f)
            {
                verticalVelocity.y = -1f;
            }

            if (characterController.isGrounded && Input.GetKeyDown(KeyCode.Space))
            {
                verticalVelocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }

            verticalVelocity.y += gravity * Time.deltaTime;
            characterController.Move(verticalVelocity * Time.deltaTime);
        }
    }
}
