package tcs.lbs.intentsniffer;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity
{
    TextView LatitudeTextView, LongitudeTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LatitudeTextView = findViewById(R.id.LatitudeTextView);
        LongitudeTextView = findViewById(R.id.LongitudeTextView);


        // TODO Define a broadcast receiver class
        // TODO Register to receive broadcast messages from ForegroundLocationService of the LocationApp
        // TODO Extract Location coordinates from the broadcast massage and show them in LatitudeTextView and LongitudeTextView
    }
}
