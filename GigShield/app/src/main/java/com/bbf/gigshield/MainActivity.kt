package com.bbf.gigshield

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import com.bbf.gigshield.navigation.NavGraph
import com.bbf.gigshield.ui.theme.GigShieldTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            GigShieldTheme {
                val navController = rememberNavController()
                NavGraph(navController = navController)
            }
        }
    }
}
