package com.bbf.gigshield.screens

import android.widget.Toast
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
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.ui.theme.GigShieldBlueInfo
import com.bbf.gigshield.ui.theme.GigShieldGray
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldGreenLight

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PayoutScreen(navController: NavHostController) {

    val context = LocalContext.current

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Payout Details", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back",
                            tint = Color.White)
                    }
                },
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
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            Spacer(modifier = Modifier.height(16.dp))

            // Success icon and amount
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = null,
                tint = GigShieldGreenLight,
                modifier = Modifier.size(80.dp)
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                "₹280.00 Credited",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                color = GigShieldGreenLight
            )
            Text(
                "Koramangala · Heavy Rain · Tue 25 Mar 2026",
                fontSize = 13.sp,
                color = GigShieldGray,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Payout breakdown card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(4.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Payout Details", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    PayoutRow("Event", "Heavy rainfall")
                    PayoutRow("Duration", "4.0 hours")
                    PayoutRow("Your hourly rate", "₹87.50")
                    PayoutRow("Coverage rate", "80%")
                    PayoutRow("Calculation", "4.0 × ₹87.50 × 80%")
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    PayoutRow("Payout amount", "₹280.00",
                        bold = true, valueColor = GigShieldGreenLight)
                    PayoutRow("Transfer to", "ravi.kumar@okaxis")
                    PayoutRow("Transaction ID", "GS-2026-03-25-4421")
                    PayoutRow("Status", "SUCCESS",
                        bold = true, valueColor = GigShieldGreenLight)
                    PayoutRow("Time", "14:17:43 IST")
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Info card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = GigShieldBlueInfo),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Info, contentDescription = null,
                            tint = Color(0xFF1565C0), modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("No action was required from you",
                            fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("This payout was triggered and processed automatically",
                        fontSize = 13.sp)
                    Text("Your policy remains active for the rest of this week",
                        fontSize = 13.sp)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Coverage remaining card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(2.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Coverage remaining this week",
                        fontSize = 13.sp, color = GigShieldGray)
                    Text("₹3,920.00 of ₹4,200.00",
                        fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { 3920f / 4200f },
                        modifier = Modifier.fillMaxWidth(),
                        color = GigShieldGreen
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { navController.navigate("live_coverage") {
                    popUpTo("live_coverage") { inclusive = true }
                }},
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GigShieldGreen),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Back to Dashboard",
                    fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedButton(
                onClick = {
                    Toast.makeText(context, "Coming in Phase 2", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("View All Payouts", fontSize = 16.sp)
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
fun PayoutRow(
    label: String,
    value: String,
    bold: Boolean = false,
    valueColor: Color = Color.Unspecified
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp)
    ) {
        Text(
            label,
            fontSize = 13.sp,
            color = GigShieldGray,
            modifier = Modifier.weight(1f)
        )
        Text(
            value,
            fontSize = 13.sp,
            fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
            color = if (valueColor != Color.Unspecified) valueColor else Color.Unspecified
        )
    }
}

