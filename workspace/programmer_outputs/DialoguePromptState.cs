using UnityEngine;

[DisallowMultipleComponent]
public sealed class DialoguePromptState : MonoBehaviour
{
    [SerializeField] private GameObject promptPanel;
    [SerializeField] private string openingLine = "Welcome, traveler.";
    [SerializeField] private string continueLine = "The ruins are just ahead.";
    [SerializeField] private string currentLine = string.Empty;
    [SerializeField] private bool isVisible;
    [SerializeField] private bool canContinue;
    [SerializeField] private bool hasCompleted;

    public GameObject PromptPanel => promptPanel;
    public string CurrentLine => currentLine;
    public bool IsVisible => isVisible;
    public bool CanContinue => canContinue;
    public bool HasCompleted => hasCompleted;

    public void Configure(GameObject targetPanel, string firstLine, string nextLine)
    {
        promptPanel = targetPanel;
        openingLine = string.IsNullOrWhiteSpace(firstLine) ? "Welcome, traveler." : firstLine;
        continueLine = string.IsNullOrWhiteSpace(nextLine) ? "The ruins are just ahead." : nextLine;
        currentLine = string.Empty;
        isVisible = false;
        canContinue = false;
        hasCompleted = false;
        SetPanelVisible(false);
    }

    public void BeginDialogue()
    {
        currentLine = openingLine;
        isVisible = true;
        canContinue = true;
        hasCompleted = false;
        SetPanelVisible(true);
        Debug.Log($"Dialogue prompt shown: {currentLine}");
    }

    public void ContinueDialogue()
    {
        currentLine = continueLine;
        isVisible = true;
        canContinue = false;
        hasCompleted = true;
        SetPanelVisible(true);
        Debug.Log($"Dialogue prompt continued: {currentLine}");
    }

    private void SetPanelVisible(bool visible)
    {
        if (promptPanel != null)
        {
            promptPanel.SetActive(visible);
        }
    }
}
