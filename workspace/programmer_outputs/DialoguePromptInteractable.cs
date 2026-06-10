using UnityEngine;

[DisallowMultipleComponent]
public sealed class DialoguePromptInteractable : InteractableObject
{
    [SerializeField] private DialoguePromptState dialogueState;

    public DialoguePromptState DialogueState => dialogueState;

    public void ConfigureDialogue(DialoguePromptState state, string npcName)
    {
        dialogueState = state;
        Configure(npcName, true);
    }

    public override void Interact()
    {
        if (!TryBeginInteract())
        {
            return;
        }

        if (dialogueState == null)
        {
            Debug.Log($"{DisplayName} cannot start dialogue because no prompt state is assigned.");
            return;
        }

        if (!dialogueState.IsVisible)
        {
            dialogueState.BeginDialogue();
            return;
        }

        if (dialogueState.CanContinue)
        {
            dialogueState.ContinueDialogue();
            return;
        }

        Debug.Log($"Dialogue already completed for {DisplayName}.");
    }
}
