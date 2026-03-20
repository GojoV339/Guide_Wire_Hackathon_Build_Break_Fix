package com.bbf.gigshield.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.ui.theme.GigShieldAlertBorder
import com.bbf.gigshield.ui.theme.GigShieldAlertYellow
import com.bbf.gigshield.ui.theme.GigShieldGray
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldGreenLight

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LiveCoverageScreen(navController: NavHostController) {
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("My Coverage", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = GigShieldGreen,
                    titleContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {

            // Policy active card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = GigShieldGreen),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("POLICY ACTIVE", fontWeight = FontWeight.Bold,
                        fontSize = 20.sp, color = Color.White)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Mon 24 Mar — Sun 30 Mar 2026",
                        fontSize = 13.sp, color = Color.White.copy(alpha = 0.8f))
                    Text("Zone: Koramangala, Bengaluru",
                        fontSize = 13.sp, color = Color.White.copy(alpha = 0.8f))
                    Text("Coverage remaining: ₹4,200.00",
                        fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Rain alert card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = GigShieldAlertYellow),
                border = BorderStroke(1.dp, GigShieldAlertBorder),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Warning, contentDescription = null,
                            tint = GigShieldAlertBorder, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Rain Alert Detected in Your Zone",
                            fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Rainfall: 32mm/hr — Threshold exceeded", fontSize = 13.sp)
                    Text("Duration: 2.5 hours", fontSize = 13.sp)
                    Text("Payout is being calculated...",
                        fontSize = 13.sp, fontStyle = FontStyle.Italic)
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth(),
                        color = GigShieldAlertBorder
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Protected hours card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(2.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Protected hours remaining: 14 hrs",
                        fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { 0.35f },
                        modifier = Modifier.fillMaxWidth(),
                        color = GigShieldGreen
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
            Text("Recent Activity", fontWeight = FontWeight.Bold, fontSize = 15.sp)
            Spacer(modifier = Modifier.height(8.dp))

            // Activity items
            val activities = listOf(
                Pair("Policy activated — ₹49.00 charged", "Mon 24 Mar, 12:00 AM"),
                Pair("Rain alert triggered in your zone", "Tue 25 Mar, 2:15 PM"),
                Pair("Fraud check passed — Trust score: 0.91", "Tue 25 Mar, 2:17 PM"),
                Pair("Payout processing...", "Tue 25 Mar, 2:17 PM")
            )

            activities.forEach { (activity, time) ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 3.dp),
                    elevation = CardDefaults.cardElevation(1.dp),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(activity, fontSize = 13.sp)
                        Text(time, fontSize = 12.sp, color = GigShieldGray)
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { navController.navigate("payout") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GigShieldGreen),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("View Payout Details", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

