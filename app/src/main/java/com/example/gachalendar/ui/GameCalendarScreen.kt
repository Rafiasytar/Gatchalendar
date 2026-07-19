package com.example.gachalendar.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.gachalendar.model.Game
import com.example.gachalendar.model.GameEvent
import java.time.LocalDateTime

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameCalendarScreen(
    game: Game,
    events: List<GameEvent>,
    onBackClick: () -> Unit,
    onEventClick: (GameEvent) -> Unit
) {
    val gameEvents = events.filter { it.gameId == game.id }
        .sortedBy { it.endTime }

    var isTimelineView by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(game.name) },
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
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = { isTimelineView = !isTimelineView },
                containerColor = MaterialTheme.colorScheme.primary,
                contentColor = MaterialTheme.colorScheme.onPrimary,
                elevation = FloatingActionButtonDefaults.elevation(defaultElevation = 8.dp)
            ) {
                Text(if (isTimelineView) "List View" else "Timeline View", fontWeight = FontWeight.Bold)
            }
        }
    ) { paddingValues ->
        if (isTimelineView) {
            TimelineView(
                events = gameEvents,
                onEventClick = onEventClick,
                modifier = Modifier.padding(paddingValues)
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    Text(
                        text = "Events & Banners",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }
                if (gameEvents.isEmpty()) {
                    item {
                        Text("No active events currently for ${game.name}.")
                    }
                } else {
                    items(gameEvents) { event ->
                        EventCard(
                            event = event,
                            onClick = { onEventClick(event) }
                        )
                    }
                }
            }
        }
    }
}
