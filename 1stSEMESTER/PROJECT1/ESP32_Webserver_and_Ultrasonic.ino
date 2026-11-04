#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
 
// ================= CONFIG =================
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASS = "YOUR_PASS";
const char* HOSTNAME  = "ultrasonic";   // http://ultrasonic.local
 
const uint8_t PIN_SIG           = 4;    // 3-pin sensor signal
const uint8_t PIN_FORCE_PRESENT = 25;
const uint8_t PIN_FORCE_ABSENT  = 26;
 
float          THRESHOLD_CM    = 150.0; // closer than this = presence
const uint16_t ECHO_TIMEOUT_US = 25000;
const uint8_t  SAMPLES         = 3;     // median filter
const uint16_t DEBOUNCE_MS     = 30;
const uint16_t READ_PERIOD_MS  = 80;
 
WebServer server(80);
 
// ================= STATE =================
float    distanceCm = -1.0;
bool     sensorOk   = false;
uint32_t lastRead   = 0;
 
struct Button {
  uint8_t  pin;
  bool     raw;
  bool     stable;
  uint32_t changedAt;
};
 
Button bPresent = { PIN_FORCE_PRESENT, false, false, 0 };
Button bAbsent  = { PIN_FORCE_ABSENT,  false, false, 0 };
 
// ================= BUTTONS =================
void initButton(Button &b) {
  pinMode(b.pin, INPUT_PULLUP);
  b.raw = b.stable = (digitalRead(b.pin) == LOW);
  b.changedAt = millis();
}
 
void updateButton(Button &b) {
  bool raw = (digitalRead(b.pin) == LOW);   // pressed = LOW
  if (raw != b.raw) { b.raw = raw; b.changedAt = millis(); }
  if (millis() - b.changedAt >= DEBOUNCE_MS) b.stable = b.raw;
}
 
// ================= ULTRASONIC (single pin) =================
float readOnce() {
  pinMode(PIN_SIG, OUTPUT);
  digitalWrite(PIN_SIG, LOW);
  delayMicroseconds(3);
  digitalWrite(PIN_SIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_SIG, LOW);
  pinMode(PIN_SIG, INPUT);                       // same pin becomes input
  uint32_t us = pulseIn(PIN_SIG, HIGH, ECHO_TIMEOUT_US);
  if (us == 0) return -1.0;                      // no echo / timeout
  return (us * 0.0343f) / 2.0f;                  // cm
}
 
void readSensor() {
  float v[SAMPLES];
  uint8_t n = 0;
  for (uint8_t i = 0; i < SAMPLES; i++) {
    float x = readOnce();
    if (x > 0) v[n++] = x;
    delay(20);
  }
  if (n == 0) { sensorOk = false; distanceCm = -1.0; return; }
  for (uint8_t i = 1; i < n; i++)                 // insertion sort, small n
    for (uint8_t j = i; j > 0 && v[j] < v[j - 1]; j--) {
      float t = v[j]; v[j] = v[j - 1]; v[j - 1] = t;
    }
  distanceCm = v[n / 2];                          // median
  sensorOk = true;
}
 
// ================= PRESENCE LOGIC =================
const char* overrideName() {
  if (bAbsent.stable)  return "force_absent";     // highest priority
  if (bPresent.stable) return "force_present";
  return "none";
}
 
bool isPresent() {
  if (bAbsent.stable)  return false;              // fail-safe: nobody
  if (bPresent.stable) return true;               // fail-safe: somebody
  return sensorOk && distanceCm > 0 && distanceCm <= THRESHOLD_CM;
}
 
// ================= HTTP HELPERS =================
void sendJson(int code, const String &body) {
  server.send(code, "application/json", body);
}
 
// ================= HANDLERS =================
void handleStatus() {
  char dist[16];
  if (sensorOk) snprintf(dist, sizeof(dist), "%.1f", distanceCm);
  else          strcpy(dist, "null");
 
  char buf[400];
  snprintf(buf, sizeof(buf),
    "{\"present\":%s,\"distance_cm\":%s,\"sensor_ok\":%s,\"threshold_cm\":%.1f,"
    "\"override\":\"%s\",\"force_present_button\":%s,\"force_absent_button\":%s,"
    "\"uptime_ms\":%lu,\"rssi\":%d}",
    isPresent() ? "true" : "false", dist, sensorOk ? "true" : "false",
    THRESHOLD_CM, overrideName(),
    bPresent.stable ? "true" : "false", bAbsent.stable ? "true" : "false",
    (unsigned long)millis(), WiFi.RSSI());
 
  sendJson(200, buf);
}
 
void handleDistance() {
  char buf[40];
  if (sensorOk) snprintf(buf, sizeof(buf), "{\"distance_cm\":%.1f}", distanceCm);
  else          strcpy(buf, "{\"distance_cm\":null}");
  sendJson(200, buf);
}
 
void handlePresence() {
  char buf[80];
  snprintf(buf, sizeof(buf), "{\"present\":%s,\"override\":\"%s\"}",
           isPresent() ? "true" : "false", overrideName());
  sendJson(200, buf);
}
 
void handleConfig() {
  if (server.hasArg("threshold_cm")) {
    float t = server.arg("threshold_cm").toFloat();
    if (t < 2.0f || t > 400.0f) {
      sendJson(400, "{\"error\":\"threshold_cm must be between 2 and 400\"}");
      return;
    }
    THRESHOLD_CM = t;
  }
  handleStatus();
}
 
void handleRoot() {
  String html = R"rawliteral(<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ultrasonic</title></head>
<body style="font-family:system-ui;padding:24px">
<h2>Sensor ultrassonico</h2>
<p>Distance: <b id="d">-</b> cm</p>
<p>Present: <b id="p">-</b></p>
<p>Override: <b id="o">-</b></p>
<script>
setInterval(async () => {
  const j = await (await fetch('/api/status')).json();
  document.getElementById('d').textContent = (j.distance_cm === null) ? 'no reading' : j.distance_cm;
  document.getElementById('p').textContent = j.present ? 'YES' : 'NO';
  document.getElementById('o').textContent = j.override;
}, 1000);
</script></body></html>)rawliteral";
  server.send(200, "text/html", html);
}
 
// ================= SETUP / LOOP =================
void setup() {
  Serial.begin(115200);
  initButton(bPresent);
  initButton(bAbsent);
  pinMode(PIN_SIG, INPUT);
 
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting");
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 20000) {
    delay(300); Serial.print(".");
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nNo WiFi, restarting in 5 s");
    delay(5000);
    ESP.restart();
  }
  Serial.print("\nIP: "); Serial.println(WiFi.localIP());
 
  if (MDNS.begin(HOSTNAME)) MDNS.addService("http", "tcp", 80);
 
  server.enableCORS(true);
  server.on("/",               HTTP_GET,  handleRoot);
  server.on("/api/status",     HTTP_GET,  handleStatus);
  server.on("/api/distance",   HTTP_GET,  handleDistance);
  server.on("/api/presence",   HTTP_GET,  handlePresence);
  server.on("/api/config",     HTTP_GET,  handleConfig);
  server.on("/api/config",     HTTP_POST, handleConfig);
  server.onNotFound([]() { sendJson(404, "{\"error\":\"not found\"}"); });
  server.begin();
}
 
void loop() {
  server.handleClient();
  updateButton(bPresent);
  updateButton(bAbsent);
 
  if (millis() - lastRead >= READ_PERIOD_MS) {
    lastRead = millis();
    readSensor();
  }
}
