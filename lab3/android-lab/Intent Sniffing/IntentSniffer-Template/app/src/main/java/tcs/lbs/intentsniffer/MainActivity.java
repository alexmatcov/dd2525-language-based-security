package tcs.lbs.intentsniffer;

import androidx.appcompat.app.AppCompatActivity;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.Location;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    LocationBroadcastReceiver mReceiver;
    TextView LatitudeTextView, LongitudeTextView;

    static final String RECEIVER_ACTION_1 = "tcs.lbs.locationapp.MainActivityReceiver";
    static final String RECEIVER_ACTION_2 = "tcs.lbs.weather_app.WeatherBroadcastReceiver";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LatitudeTextView = findViewById(R.id.LatitudeTextView);
        LongitudeTextView = findViewById(R.id.LongitudeTextView);
    }

    @Override
    protected void onResume() {
        super.onResume();

        IntentFilter filter = new IntentFilter();
        filter.addAction(RECEIVER_ACTION_1);
        filter.addAction(RECEIVER_ACTION_2);

        mReceiver = new LocationBroadcastReceiver();
        registerReceiver(mReceiver, filter);
    }

    @Override
    protected void onStop() {
        super.onStop();
        unregisterReceiver(mReceiver);
    }

    public class LocationBroadcastReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            Location location = intent.getParcelableExtra("Location");

            if (location != null) {
                LatitudeTextView.setText("Latitude: " + location.getLatitude());
                LongitudeTextView.setText("Longitude: " + location.getLongitude());
            }
        }
    }
}