using System;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIDialoguePromptSceneValidator
{
    private const string ScenePath = "Assets/Scenes/DialoguePromptScene.unity";

    public static void ValidateScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var player = RequireObject("AIDialogue_Player");
        RequireComponent<InteractSystem>(player, "AIDialogue_Player");
        var trigger = RequireComponent<SphereCollider>(player, "AIDialogue_Player");
        if (!trigger.isTrigger)
        {
            throw new InvalidOperationException("AIDialogue_Player SphereCollider must be a trigger.");
        }

        var body = RequireComponent<Rigidbody>(player, "AIDialogue_Player");
        if (!body.isKinematic)
        {
            throw new InvalidOperationException("AIDialogue_Player Rigidbody must be kinematic.");
        }

        RequireObject("AIDialogue_Ground");
        RequireObject("AIDialogue_PlayerMarker");
        RequireObject("AIDialogue_NpcVisual");
        var npc = RequireObject("AIDialogue_Npc");
        var state = RequireComponent<DialoguePromptState>(npc, "AIDialogue_Npc");
        var interactable = RequireComponent<DialoguePromptInteractable>(npc, "AIDialogue_Npc");
        var promptPanel = state.PromptPanel;

        if (promptPanel == null || promptPanel.name != "AIDialogue_PromptPanel")
        {
            throw new InvalidOperationException("Dialogue prompt state must reference the prompt panel.");
        }

        if (interactable.DialogueState != state)
        {
            throw new InvalidOperationException("Dialogue interactable must reference the dialogue state.");
        }

        if (interactable.DisplayName != "Guide NPC")
        {
            throw new InvalidOperationException("NPC prompt should identify Guide NPC.");
        }

        if (promptPanel.activeSelf || state.IsVisible || state.CanContinue || state.HasCompleted)
        {
            throw new InvalidOperationException("Dialogue scene must start with a hidden prompt.");
        }

        interactable.Interact();
        if (!state.IsVisible || !state.CanContinue)
        {
            throw new InvalidOperationException("First interaction must open the dialogue prompt.");
        }

        if (state.CurrentLine != "Welcome, traveler.")
        {
            throw new InvalidOperationException("First dialogue line is incorrect.");
        }

        if (!promptPanel.activeSelf)
        {
            throw new InvalidOperationException("Prompt panel should become visible when dialogue starts.");
        }

        interactable.Interact();
        if (state.CanContinue || !state.HasCompleted)
        {
            throw new InvalidOperationException("Second interaction must consume the single continue action.");
        }

        if (state.CurrentLine != "The ruins are just ahead.")
        {
            throw new InvalidOperationException("Continue dialogue line is incorrect.");
        }

        if (!promptPanel.activeSelf)
        {
            throw new InvalidOperationException("Prompt panel should remain visible after continuing dialogue.");
        }

        Debug.Log("AIDialoguePromptSceneValidator passed.");
    }

    private static GameObject RequireObject(string objectName)
    {
        var found = GameObject.Find(objectName);
        if (found == null)
        {
            throw new InvalidOperationException($"Required scene object is missing: {objectName}");
        }

        return found;
    }

    private static T RequireComponent<T>(GameObject target, string objectName) where T : Component
    {
        var component = target.GetComponent<T>();
        if (component == null)
        {
            throw new InvalidOperationException($"{objectName} is missing required component {typeof(T).Name}.");
        }

        return component;
    }
}
