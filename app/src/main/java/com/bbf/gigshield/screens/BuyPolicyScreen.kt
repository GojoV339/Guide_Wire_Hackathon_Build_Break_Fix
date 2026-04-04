package com.bbf.gigshield.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.network.ApiClient
import com.bbf.gigshield.network.PolicyCreateRequestDto
import com.bbf.gigshield.network.WorkerProfileResponseDto
import com.bbf.gigshield.ui.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BuyPolicyScreen(navController: NavHostController) {
    val context = LocalContext.current
    var profile by remember { mutableStateOf<WorkerProfileResponseDto?>(null) }
    var premiumQuote by remember { mutableStateOf<com.bbf.gigshield.network.PremiumQuoteResponseDto?>(null) }
    var loading by remember { mutableStateOf(true) }
    var actLoading by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        try {
            val response = ApiClient.getAuthApi(context).getProfile()
            if (response.isSuccessful) {
                profile = response.body()
                profile?.let { p ->
                    val quoteResponse = ApiClient.getAuthApi(context).getPremiumQuote(
                        zonePincode = p.homeZonePincode ?: "",
                        zoneName = p.homeZoneName ?: ""
                    )
                    if (quoteResponse.isSuccessful) {
                        premiumQuote = quoteResponse.body()
                    }
                }
            }
        } catch (e: Exception) {
            // Error handling
        } finally {
            loading = false
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Buy Policy", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color(0xFF1B5E20),
                    titleContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        if (loading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color(0xFF1B5E20))
            }
        } else if (profile != null && premiumQuote != null) {
            val p = profile!!
            val q = premiumQuote!!
            val basePremium = q.basePremium
            val dailyEarnings = p.dailyEarningsDeclared
            val earningsLinked = q.earningsLinked
            val riskScore = q.riskScore
            val zoneRiskLoading = q.zoneRiskLoading
            val totalPremium = q.totalPremium

            Column(
                modifier = Modifier
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(16.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            tint = Color(0xFF1B5E20),
                            modifier = Modifier.size(42.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(p.name ?: "Worker", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                            Text(
                                "${p.homeZoneName ?: p.homeZonePincode}, India",
                                fontSize = 13.sp,
                                color = Color.Gray
                            )
                            Text(
                                "${p.platformPartnerId ?: "Delivery"} Partner",
                                fontSize = 13.sp,
                                color = Color.Gray
                            )
                            Text(
                                "Daily earnings: ₹${"%.0f".format(dailyEarnings)}",
                                fontSize = 13.sp,
                                color = Color.Gray
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF3E0))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("AI Risk Score", fontSize = 13.sp, color = Color.Gray)
                        Text(
                            "${"%.1f".format(riskScore)} / 10",
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFE65100)
                        )
                        Text(
                            q.riskReasoning ?: p.riskReasoning ?: "Dynamic calculation active",
                            fontSize = 12.sp,
                            color = Color.Gray,
                            lineHeight = 16.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Premium Breakdown", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                        Spacer(modifier = Modifier.height(10.dp))
                        PremiumRow("Base premium", "₹${"%.2f".format(basePremium)}")
                        PremiumRow("Earnings-linked", "₹${"%.2f".format(earningsLinked)}")
                        PremiumRow("Zone risk loading", "₹${"%.2f".format(zoneRiskLoading)}")
                        if (q.claimsSurcharge > 0) {
                            PremiumRow("Prior claims surcharge", "₹${"%.2f".format(q.claimsSurcharge)}")
                        }
                        HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                        PremiumRow(
                            "Total weekly premium",
                            "₹${"%.2f".format(totalPremium)}",
                            bold = true,
                            valueColor = Color(0xFF2E7D32)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = {
                        if (actLoading) return@Button
                        scope.launch {
                            actLoading = true
                            try {
                                val req = PolicyCreateRequestDto(
                                    zonePincode = p.homeZonePincode ?: "",
                                    zoneName = p.homeZoneName
                                )
                                val res = ApiClient.getAuthApi(context).createPolicy(req)
                                if (res.isSuccessful || res.code() == 400) {
                                    // 400 means they already have a policy this week.
                                    navController.navigate("live_coverage")
                                } else {
                                    android.widget.Toast.makeText(context, "Failed to activate policy", android.widget.Toast.LENGTH_SHORT).show()
                                }
                            } catch (e: Exception) {
                                android.widget.Toast.makeText(context, "Network Error", android.widget.Toast.LENGTH_SHORT).show()
                            } finally {
                                actLoading = false
                            }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    if (actLoading) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                    } else {
                        Text("Activate Policy — ₹${"%.2f".format(totalPremium)}", fontWeight = FontWeight.Bold)
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun PremiumRow(label: String, value: String, bold: Boolean = false, valueColor: Color = Color.Unspecified) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, fontSize = 13.sp, fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal)
        Text(value, fontSize = 13.sp, fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal, color = valueColor)
    }
}
