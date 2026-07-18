package com.example.gachalendar.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.gachalendar.model.GameEvent
import java.time.LocalDateTime
import java.time.temporal.ChronoUnit
import coil.compose.AsyncImage
import androidx.compose.ui.layout.ContentScale
import androidx.compose.foundation.clickable
import androidx.compose.foundation.background
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.Alignment

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CombinedCalendarScreen(
    events: List<GameEvent>,
    onBackClick: () -> Unit,
    onEventClick: (GameEvent) -> Unit
) {
    // Sort events by end time (closest to ending first)
    val activeEvents = events
        .filter { it.endTime.isAfter(LocalDateTime.now()) }
        .sortedBy { it.endTime }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Combined Calendar") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text(
                    text = "Active Events & Banners",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            if (activeEvents.isEmpty()) {
                item {
                    Text("No active events currently.")
                }
            } else {
                items(activeEvents) { event ->
                    EventCard(
                        event = event,
                        onClick = { onEventClick(event) }
                    )
                }
            }
        }
    }
}

@Composable
fun EventCard(event: GameEvent, onClick: () -> Unit = {}) {
    val now = LocalDateTime.now()
    val daysLeft = ChronoUnit.DAYS.between(now, event.endTime)
    val hoursLeft = ChronoUnit.HOURS.between(now, event.endTime) % 24

    val timeLeftText = if (daysLeft > 0) {
        "$daysLeft days $hoursLeft hrs left"
    } else if (hoursLeft > 0) {
        "$hoursLeft hrs left"
    } else {
        "Ending soon!"
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp)
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = MaterialTheme.shapes.medium
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Background Image
            if (event.imageUrl != null) {
                AsyncImage(
                    model = event.imageUrl,
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
                
                // Gradient overlay for text readability
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.8f)),
                                startY = 100f
                            )
                        )
                )
            } else {
                // Fallback background if no image
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.secondaryContainer)
                )
            }

            // Time left badge (Top Right)
            Surface(
                color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.9f),
                shape = MaterialTheme.shapes.small,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(8.dp)
            ) {
                Text(
                    text = timeLeftText,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }

            // Event Details (Bottom)
            Column(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    text = event.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (event.imageUrl != null) Color.White else MaterialTheme.colorScheme.onSecondaryContainer,
                    maxLines = 1
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Game: ${event.gameId.uppercase()} | Type: ${event.type.name.replace("_", " ")}",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (event.imageUrl != null) Color.LightGray else MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f)
                )
            }
        }
    }
}
