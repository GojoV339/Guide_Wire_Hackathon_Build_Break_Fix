package com.bbf.gigshield.network

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT

interface AuthApi {
    @POST("auth/send-otp")
    suspend fun sendOtp(@Body body: OtpRequestDto): Response<SendOtpResponseDto>

    @POST("auth/verify-otp")
    suspend fun verifyOtp(@Body body: OtpVerifyDto): Response<TokenResponseDto>

    @PUT("workers/profile")
    suspend fun updateProfile(@Body body: WorkerProfileUpdateDto): Response<Unit>

    @GET("workers/profile")
    suspend fun getProfile(): Response<WorkerProfileResponseDto>
}

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
