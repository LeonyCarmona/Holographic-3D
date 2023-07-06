using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class AudioRecorder : MonoBehaviour, IPointerDownHandler, IPointerUpHandler
{
    public Button recordButton;
    public AudioSource audioSource;  // Audio source to play the server response

    private AudioClip audioClip;
    private bool isRecording = false;

    private void Start()
    {
        recordButton.gameObject.AddComponent<EventTrigger>();
    }

    public void OnPointerDown(PointerEventData eventData)
    {
        if (!isRecording)
        {
            isRecording = true;
            audioClip = Microphone.Start(null, false, 10, 44100);
        }
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        if (isRecording)
        {
            Microphone.End(null);
            isRecording = false;
            SaveAudioClip();
            StartCoroutine(Upload());
        }
    }

    private void SaveAudioClip()
    {
        var audioData = new float[audioClip.samples * audioClip.channels];
        audioClip.GetData(audioData, 0);

        var byteArray = new byte[audioData.Length * 4];
        System.Buffer.BlockCopy(audioData, 0, byteArray, 0, byteArray.Length);

        string filePath = Path.Combine(Application.dataPath, "audio.pcm");
        File.WriteAllBytes(filePath, byteArray);
    }

    IEnumerator Upload()
{
    byte[] audioBytes = File.ReadAllBytes(Path.Combine(Application.dataPath, "audio.pcm"));
    WWWForm form = new WWWForm();
    form.AddBinaryData("file", audioBytes, "audio.pcm", "audio/pcm");

    UnityWebRequest www = UnityWebRequest.Post("http://127.0.0.1:5000/upload", form);
    yield return www.SendWebRequest();

    if (www.result != UnityWebRequest.Result.Success)
    {
        Debug.Log(www.error);
    }
    else
    {
        string audioUrl = www.downloadHandler.text.Trim(new char[] {'"', '\\'});
        Debug.Log("Transcript: " + audioUrl);
        StartCoroutine(DownloadAudio(audioUrl));
    }
}


    IEnumerator DownloadAudio(string audioUrl)
    {
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(audioUrl, AudioType.WAV))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = clip;
                audioSource.Play();
            }
            else
            {
                Debug.Log(www.error);
            }
        }
    }
}
