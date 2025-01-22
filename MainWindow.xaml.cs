using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;

namespace MonitorApp
{
    public partial class MainWindow : Window
    {
        private bool isMonitoring = false; // İzleme durumu
        private HashSet<string> notifiedEmails = new HashSet<string>(); // Bildirim gönderilen e-postalar

        public MainWindow()
        {
            InitializeComponent();
        }

        // "Monitor Etmeye Başla" butonuna tıklama olayı
        private async void StartMonitoring_Click(object sender, RoutedEventArgs e)
        {
            if (isMonitoring)
            {
                MessageBox.Show("Zaten çalışıyor.");
                return;
            }

            string apiKey = ApiKeyTextBox.Text;
            string domain = DomainTextBox.Text;
            string notificationEmail = NotificationEmailTextBox.Text;
            int interval = int.TryParse(IntervalTextBox.Text, out int value) ? value : 5;

            if (string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(domain) || string.IsNullOrEmpty(notificationEmail))
            {
                MessageBox.Show("Tüm alanları doldurun.");
                return;
            }

            isMonitoring = true;
            StatusTextBlock.Text = "İzleme başladı...";
            await Task.Run(() => MonitorLeak(apiKey, domain, notificationEmail, interval));
        }

        // İzleme ve API ile veri çekme
        private async void MonitorLeak(string apiKey, string domain, string notificationEmail, int interval)
        {
            while (isMonitoring)
            {
                try
                {
                    using HttpClient client = new HttpClient();
                    client.DefaultRequestHeaders.Add("Authorization", apiKey);

                    var payload = new { domain = domain };
                    var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

                    HttpResponseMessage response = await client.PostAsync("http://188.34.204.202:5000/get-data", content);
                    if (!response.IsSuccessStatusCode)
                    {
                        UpdateStatus($"API Hatası: {response.StatusCode}");
                        return;
                    }

                    string responseBody = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ApiResponse>(responseBody);

                    if (result.Data != null)
                    {
                        foreach (var entry in result.Data)
                        {
                            if (!notifiedEmails.Contains(entry.Email))
                            {
                                // E-posta gönderimini devre dışı bıraktık
                                SimulateEmail(entry.Email, "Sızıntı Tespiti", GenerateEmailContent(entry.Email));
                                SimulateEmail(notificationEmail, "Sızıntı Tespiti", $"Sızıntı tespit edildi: {entry.Email}");

                                notifiedEmails.Add(entry.Email);
                                UpdateNotificationList(entry.Email);
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    UpdateStatus($"Hata: {ex.Message}");
                }

                Thread.Sleep(TimeSpan.FromMinutes(interval));
            }
        }

        // E-posta gönderimini simüle etme (gerçek gönderim devre dışı)
        private void SimulateEmail(string recipient, string subject, string body)
        {
            Console.WriteLine($"E-posta simüle edildi: {recipient}, Konu: {subject}, İçerik: {body}");
        }

        // E-posta içeriği oluşturma
        private string GenerateEmailContent(string email)
        {
            return $"Akademik e-posta adresinize ait parolanın sızdırıldığı tespit edildi: {email}.\nLütfen en kısa sürede parolanızı değiştirin.";
        }

        // Durum mesajını güncelle
        private void UpdateStatus(string message)
        {
            Dispatcher.Invoke(() => StatusTextBlock.Text = message);
        }

        // Bildirim gönderilen e-postaları listeye ekle
        private void UpdateNotificationList(string email)
        {
            Dispatcher.Invoke(() => NotificationListBox.Items.Add(email));
        }
    }

    // API'den gelen veri sınıfları
    public class ApiResponse
    {
        public List<UserEntry> Data { get; set; }
    }

    public class UserEntry
    {
        public string Email { get; set; }
        public string Username { get; set; }
        public string DatabaseName { get; set; }
    }
}
