package com.bbf.gigshield.network

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Query

interface AuthApi {
    @POST("auth/send-otp")
    suspend fun sendOtp(@Body body: OtpRequestDto): Response<SendOtpResponseDto>

    @POST("auth/verify-otp")
    suspend fun verifyOtp(@Body body: OtpVerifyDto): Response<TokenResponseDto>

    @PUT("workers/profile")
    suspend fun updateProfile(@Body body: WorkerProfileUpdateDto): Response<Unit>

    @GET("workers/profile")
    suspend fun getProfile(): Response<WorkerProfileResponseDto>

    @GET("policies/premium-quote")
    suspend fun getPremiumQuote(
        @Query("zone_pincode") zonePincode: String,
        @Query("zone_name") zoneName: String = ""
    ): Response<PremiumQuoteResponseDto>

    @POST("policies/create")
    suspend fun createPolicy(@Body body: PolicyCreateRequestDto): Response<Any>

    @GET("workers/dashboard")
    suspend fun getDashboard(): Response<DashboardResponseDto>
}

data class PremiumQuoteResponseDto(
    @SerializedName("base_premium") val basePremium: Double,
    @SerializedName("earnings_linked") val earningsLinked: Double,
    @SerializedName("zone_risk_loading") val zoneRiskLoading: Double,
    @SerializedName("claims_surcharge") val claimsSurcharge: Double,
    @SerializedName("total_premium") val totalPremium: Double,
    @SerializedName("max_coverage") val maxCoverage: Double,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("risk_category") val riskCategory: String,
    @SerializedName("risk_reasoning") val riskReasoning: String
)

data class WorkerProfileResponseDto(
    val id: String,
    val name: String?,
    @SerializedName("home_zone_pincode") val homeZonePincode: String?,
    @SerializedName("home_zone_name") val homeZoneName: String?,
    @SerializedName("daily_earnings_declared") val dailyEarningsDeclared: Double,
    @SerializedName("upi_id") val upiId: String?,
    @SerializedName("platform_partner_id") val platformPartnerId: String?,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("risk_reasoning") val riskReasoning: String?
)

data class PolicyCreateRequestDto(
    @SerializedName("zone_pincode") val zonePincode: String,
    @SerializedName("zone_name") val zoneName: String?
)

data class DashboardResponseDto(
    @SerializedName("worker_name") val workerName: String?,
    @SerializedName("risk_score") val riskScore: Double,
    @SerializedName("active_policy") val activePolicy: ActivePolicyDto?,
    @SerializedName("recent_claims") val recentClaims: List<RecentClaimDto>,
    @SerializedName("active_disruptions") val activeDisruptions: List<ActiveDisruptionDto>,
    @SerializedName("total_received_this_month") val totalReceivedThisMonth: Double
)

data class ActivePolicyDto(
    val id: String,
    @SerializedName("coverage_remaining") val coverageRemaining: Double,
    @SerializedName("max_coverage") val maxCoverage: Double,
    @SerializedName("week_end") val weekEnd: String,
    val status: String
)

data class RecentClaimDto(
    val id: String,
    val status: String,
    val amount: Double,
    @SerializedName("created_at") val createdAt: String
)

data class ActiveDisruptionDto(
    val id: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("severity_value") val severityValue: Double,
    @SerializedName("api_source") val apiSource: String,
    @SerializedName("created_at") val createdAt: String
)
