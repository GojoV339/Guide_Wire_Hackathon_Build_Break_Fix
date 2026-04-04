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
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.network.ApiClient
import androidx.compose.runtime.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.ui.platform.LocalContext
import androidx.compose.material3.CircularProgressIndicator
import kotlinx.coroutines.launch
import com.bbf.gigshield.ui.theme.GigShieldAlertBorder
import com.bbf.gigshield.ui.theme.GigShieldAlertYellow
import com.bbf.gigshield.ui.theme.GigShieldGray
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldAmber

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LiveCoverageScreen(navController: NavHostController) {
    val context = LocalContext.current
    var dashboard by remember { mutableStateOf<com.bbf.gigshield.network.DashboardResponseDto?>(null) }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        try {
            val response = ApiClient.getAuthApi(context).getDashboard()
            if (response.isSuccessful) {
                dashboard = response.body()
            }
        } catch (e: Exception) {
            // handle error
        } finally {
            loading = false
        }
    }

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
        if (loading) {
            Column(modifier = Modifier.padding(paddingValues).fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
                Spacer(modifier = Modifier.height(32.dp))
                CircularProgressIndicator(color = GigShieldGreen)
            }
        } else if (dashboard == null || dashboard!!.activePolicy == null) {
            Column(modifier = Modifier.padding(paddingValues).padding(16.dp)) {
                Text("No active policy found. Head to the dashboard to purchase one.", fontSize = 16.sp)
            }
        } else {
            val d = dashboard!!
            val pol = d.activePolicy!!
            
            Column(
                modifier = Modifier
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = GigShieldGreen),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("POLICY ACTIVE", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = Color.White)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "Ends ${pol.weekEnd}",
                            fontSize = 13.sp,
                            color = Color.White.copy(alpha = 0.8f)
                        )
                        Text(
                            "Coverage remaining: ₹${"%.0f".format(pol.coverageRemaining)}",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                if (d.activeDisruptions.isNotEmpty()) {
                    d.activeDisruptions.forEach { dist ->
                        Card(
                            modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                            colors = CardDefaults.cardColors(containerColor = GigShieldAlertYellow),
                            border = BorderStroke(1.dp, GigShieldAlertBorder),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Default.Warning,
                                        contentDescription = null,
                                        tint = GigShieldAlertBorder,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        "${dist.eventType.uppercase()} Alert Detected",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 14.sp
                                    )
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text("Severity: ${dist.severityValue}", fontSize = 13.sp)
                                Text("Source: ${dist.apiSource}", fontSize = 13.sp)
                                Text(
                                    "Payout being automatically calculated...",
                                    fontSize = 13.sp,
                                    fontStyle = FontStyle.Italic
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                LinearProgressIndicator(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = GigShieldAlertBorder
                                )
                            }
                        }
                    }
                } else {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                         Column(modifier = Modifier.padding(16.dp)) {
                             Text("No active disruptions detected in your zone.", fontSize = 14.sp, color = GigShieldGray)
                         }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            "Protected coverage remaining: ₹${"%.0f".format(pol.coverageRemaining)} / ₹${"%.0f".format(pol.maxCoverage)}",
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        val progress = if (pol.maxCoverage > 0) (pol.coverageRemaining / pol.maxCoverage).toFloat() else 0f
                        LinearProgressIndicator(
                            progress = { progress },
                            modifier = Modifier.fillMaxWidth(),
                            color = GigShieldGreen
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Text("Recent Activity", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                Spacer(modifier = Modifier.height(8.dp))

                if (d.recentClaims.isEmpty()) {
                    Text("No recent claims.", fontSize = 13.sp, color = Color.Gray)
                } else {
                    d.recentClaims.forEach { claim ->
                        ActivityItem(title = "Claim ${claim.status} — ₹${"%.0f".format(claim.amount)}", time = claim.createdAt)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // The next navigation logic
                // Provide a button if they need to see more
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
private fun ActivityItem(title: String, time: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 3.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(text = title, fontSize = 13.sp)
            Text(text = time, fontSize = 12.sp, color = GigShieldGray)
        }
    }
}

