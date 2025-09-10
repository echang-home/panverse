"""
Watchdog Service - AI Content Generation Monitoring Service

This module provides monitoring and quality assurance for AI-generated content,
preventing AI drift, fallbacks, and ensuring consistent high-quality output.

Key responsibilities:
1. Monitor AI API calls and responses
2. Track metrics and costs
3. Detect AI drift and fallbacks
4. Ensure content quality
5. Alert on issues
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable

# Set up logging
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severity levels for alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to track"""
    GENERATION_TIME = "generation_time"
    QUALITY_SCORE = "quality_score"
    API_LATENCY = "api_latency"
    TOKEN_USAGE = "token_usage"
    ERROR_RATE = "error_rate"
    REGENERATION_RATE = "regeneration_rate"
    COST = "cost"


@dataclass
class Alert:
    """System alert"""
    message: str
    severity: AlertSeverity
    source: str
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class Metric:
    """A single metric data point"""
    metric_type: MetricType
    value: float
    component: str
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)


class ContentVerifier:
    """
    Verifies AI-generated content to prevent drift and fallbacks

    This class implements detection strategies for common AI issues:
    1. Empty/stub content detection
    2. Fallback text detection (e.g., "I'm sorry, I can't...")
    3. Template text detection (placeholder responses)
    4. Content formatting verification
    """

    def __init__(self):
        """Initialize the content verifier"""
        # Fallback phrases that indicate AI is drifting
        self.fallback_phrases = [
            "I'm sorry, I cannot",
            "I apologize, but I",
            "I don't have enough information",
            "As an AI language model",
            "I cannot generate",
            "I cannot create",
            "I cannot provide",
            "Unable to generate",
            "Unable to create",
            "Unable to provide",
        ]

        # Placeholder templates that indicate incomplete generation
        self.placeholder_patterns = [
            "{placeholder}",
            "[Insert",
            "[placeholder",
            "PLACEHOLDER",
            "TODO:",
            "<placeholder>",
            "<insert",
        ]

        logger.info("ContentVerifier initialized with detection patterns")

    def verify_content(self, content: str, content_type: str) -> Tuple[bool, List[str]]:
        """
        Verify AI-generated content for issues

        Args:
            content: The generated content to verify
            content_type: Type of content being verified

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for empty content
        if not content or len(content.strip()) < 10:
            issues.append(f"Empty or too short {content_type} content")
            return False, issues

        # Check for fallback phrases
        for phrase in self.fallback_phrases:
            if phrase.lower() in content.lower():
                issues.append(f"Fallback phrase detected: '{phrase}'")

        # Check for placeholder patterns
        for pattern in self.placeholder_patterns:
            if pattern.lower() in content.lower():
                issues.append(f"Placeholder text detected: '{pattern}'")

        # Content-specific validation
        if content_type == "monster":
            if not self._validate_monster_content(content):
                issues.append("Monster content format validation failed")
        elif content_type == "location":
            if not self._validate_location_content(content):
                issues.append("Location content format validation failed")
        elif content_type == "npc":
            if not self._validate_npc_content(content):
                issues.append("NPC content format validation failed")

        return len(issues) == 0, issues

    def _validate_monster_content(self, content: str) -> bool:
        """Validate monster content formatting"""
        # Check for stat block elements
        required_elements = [
            "armor class",
            "hit points",
            "speed",
            "str",
            "dex",
            "con",
        ]

        content_lower = content.lower()
        found_elements = sum(1 for elem in required_elements if elem in content_lower)

        # Need at least 4 of 6 elements to be valid
        return found_elements >= 4

    def _validate_location_content(self, content: str) -> bool:
        """Validate location content formatting"""
        # Check for description elements
        required_elements = [
            "description",
            "features",
            "location",
            "area",
        ]

        content_lower = content.lower()
        found_elements = sum(1 for elem in required_elements if elem in content_lower)

        # Need at least 2 of 4 elements to be valid
        return found_elements >= 2

    def _validate_npc_content(self, content: str) -> bool:
        """Validate NPC content formatting"""
        # Check for NPC elements
        required_elements = [
            "description",
            "personality",
            "appearance",
            "motivation",
        ]

        content_lower = content.lower()
        found_elements = sum(1 for elem in required_elements if elem in content_lower)

        # Need at least 2 of 4 elements to be valid
        return found_elements >= 2


class WatchdogService:
    """
    Watchdog service for monitoring AI generation

    This class provides monitoring, metrics tracking, and quality assurance
    for AI-generated content. It prevents AI drift, detects fallbacks,
    and ensures consistent high-quality output.
    """

    def __init__(self, metrics_path: str = "data/metrics", alert_threshold: int = 3):
        """
        Initialize the Watchdog service

        Args:
            metrics_path: Path to save metrics data
            alert_threshold: Number of consecutive errors before critical alert
        """
        self.metrics_path = metrics_path
        self.alert_threshold = alert_threshold
        self.content_verifier = ContentVerifier()

        # Create metrics directory if it doesn't exist
        os.makedirs(metrics_path, exist_ok=True)

        # Initialize metrics and alerts storage
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.error_count = 0

        # API usage tracking
        self.api_calls = {
            "claude": 0,
            "chatgpt": 0,
            "dalle": 0,
        }

        # Cost tracking
        self.cost_estimates = {
            "claude": 0.0,
            "chatgpt": 0.0,
            "dalle": 0.0,
            "total": 0.0,
        }

        # Callbacks for alerts
        self.alert_callbacks: List[Callable[[Alert], None]] = []

        logger.info(f"WatchdogService initialized with metrics path: {metrics_path}")

    def register_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """
        Register a callback for alerts

        Args:
            callback: Function to call when an alert is generated
        """
        self.alert_callbacks.append(callback)
        logger.info(f"Registered alert callback: {callback.__name__}")

    def track_metric(self, metric_type: MetricType, value: float, component: str, details: Dict[str, Any] = None) -> None:
        """
        Track a metric

        Args:
            metric_type: Type of metric
            value: Metric value
            component: Component being measured
            details: Additional details
        """
        timestamp = time.time()
        metric = Metric(
            metric_type=metric_type,
            value=value,
            component=component,
            timestamp=timestamp,
            details=details or {},
        )

        self.metrics.append(metric)

        # Save metrics periodically (every 10 metrics)
        if len(self.metrics) % 10 == 0:
            self._save_metrics()

        logger.debug(f"Tracked metric: {metric_type.value} = {value} for {component}")

    def track_api_call(self, api_name: str, token_count: int, response_time: float, cost: float = None) -> None:
        """
        Track an API call

        Args:
            api_name: Name of the API (claude, chatgpt, dalle)
            token_count: Number of tokens used
            response_time: Response time in seconds
            cost: Estimated cost of the call
        """
        # Update API call counts
        if api_name in self.api_calls:
            self.api_calls[api_name] += 1
        else:
            self.api_calls[api_name] = 1

        # Track token usage metric
        self.track_metric(
            metric_type=MetricType.TOKEN_USAGE,
            value=token_count,
            component=api_name,
            details={"timestamp": time.time()}
        )

        # Track API latency metric
        self.track_metric(
            metric_type=MetricType.API_LATENCY,
            value=response_time,
            component=api_name,
            details={"timestamp": time.time()}
        )

        # Track cost if provided
        if cost is not None:
            self.track_metric(
                metric_type=MetricType.COST,
                value=cost,
                component=api_name,
                details={"timestamp": time.time()}
            )

            # Update cost estimates
            if api_name in self.cost_estimates:
                self.cost_estimates[api_name] += cost
            else:
                self.cost_estimates[api_name] = cost

            self.cost_estimates["total"] += cost

        logger.info(f"API call: {api_name}, tokens: {token_count}, time: {response_time:.2f}s, cost: {cost}")

    def verify_ai_response(self, content: str, content_type: str, source: str) -> Tuple[bool, List[str]]:
        """
        Verify AI-generated content

        Args:
            content: The content to verify
            content_type: Type of content
            source: Source of the content (e.g., "claude", "chatgpt")

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        # Verify content using content verifier
        is_valid, issues = self.content_verifier.verify_content(content, content_type)

        # Track error rate if invalid
        if not is_valid:
            self.error_count += 1
            self.track_metric(
                metric_type=MetricType.ERROR_RATE,
                value=1.0,
                component=source,
                details={"issues": issues, "content_type": content_type}
            )

            # Create alert if needed
            if issues:
                severity = AlertSeverity.WARNING
                if self.error_count >= self.alert_threshold:
                    severity = AlertSeverity.CRITICAL

                self._create_alert(
                    message=f"Content verification failed for {content_type}",
                    severity=severity,
                    source=source,
                    details={"issues": issues, "content_type": content_type}
                )
        else:
            # Reset error count on success
            self.error_count = 0
            self.track_metric(
                metric_type=MetricType.ERROR_RATE,
                value=0.0,
                component=source,
                details={"content_type": content_type}
            )

        return is_valid, issues

    def check_for_fallbacks(self, generation_func, *args, **kwargs) -> Tuple[Any, bool]:
        """
        Check for fallbacks in generation function

        This decorator-like function wraps a generation function and checks
        its output for fallbacks or hardcoded responses.

        Args:
            generation_func: Function that generates content
            *args, **kwargs: Arguments to pass to generation_func

        Returns:
            Tuple of (generation_result, is_fallback)
        """
        try:
            # Call the generation function
            result = generation_func(*args, **kwargs)

            # Check if result is a string (direct content)
            if isinstance(result, str):
                content = result
            # If result is a dict, look for content field
            elif isinstance(result, dict) and "content" in result:
                content = result["content"]
            else:
                # Unknown result format, consider it valid
                return result, False

            # Check for fallback phrases
            for phrase in self.content_verifier.fallback_phrases:
                if phrase.lower() in content.lower():
                    # Create alert for fallback
                    self._create_alert(
                        message=f"Fallback detected in generation",
                        severity=AlertSeverity.ERROR,
                        source="generator",
                        details={"fallback_phrase": phrase}
                    )
                    return result, True

            # Check for placeholder patterns
            for pattern in self.content_verifier.placeholder_patterns:
                if pattern.lower() in content.lower():
                    # Create alert for placeholder
                    self._create_alert(
                        message=f"Placeholder detected in generation",
                        severity=AlertSeverity.ERROR,
                        source="generator",
                        details={"placeholder_pattern": pattern}
                    )
                    return result, True

            # All checks passed
            return result, False

        except Exception as e:
            # Create alert for exception
            self._create_alert(
                message=f"Exception in generation function: {str(e)}",
                severity=AlertSeverity.ERROR,
                source="generator",
                details={"exception": str(e)}
            )
            # Re-raise the exception
            raise

    def track_quality_score(self, component: str, score: float, details: Dict[str, Any] = None) -> None:
        """
        Track a quality score

        Args:
            component: Component being scored
            score: Quality score (0.0 to 1.0)
            details: Additional details
        """
        self.track_metric(
            metric_type=MetricType.QUALITY_SCORE,
            value=score,
            component=component,
            details=details or {}
        )

        # Create alert if quality is too low
        if score < 0.5:
            self._create_alert(
                message=f"Low quality score for {component}: {score:.2f}",
                severity=AlertSeverity.WARNING,
                source="quality_checker",
                details=details or {}
            )

    def get_api_usage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of API usage

        Returns:
            Dictionary with API usage statistics
        """
        # Calculate average token usage by API
        token_metrics = [m for m in self.metrics if m.metric_type == MetricType.TOKEN_USAGE]
        token_usage_by_api = {}

        for api in self.api_calls.keys():
            api_metrics = [m for m in token_metrics if m.component == api]
            if api_metrics:
                avg_tokens = sum(m.value for m in api_metrics) / len(api_metrics)
                token_usage_by_api[api] = {
                    "total_calls": self.api_calls[api],
                    "avg_tokens_per_call": avg_tokens,
                    "estimated_cost": self.cost_estimates.get(api, 0.0),
                }
            else:
                token_usage_by_api[api] = {
                    "total_calls": self.api_calls.get(api, 0),
                    "avg_tokens_per_call": 0,
                    "estimated_cost": self.cost_estimates.get(api, 0.0),
                }

        return {
            "total_calls": sum(self.api_calls.values()),
            "calls_by_api": self.api_calls,
            "token_usage": token_usage_by_api,
            "total_estimated_cost": self.cost_estimates["total"],
        }

    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Get a summary of quality metrics

        Returns:
            Dictionary with quality statistics
        """
        # Calculate average quality score by component
        quality_metrics = [m for m in self.metrics if m.metric_type == MetricType.QUALITY_SCORE]
        quality_by_component = {}

        components = set(m.component for m in quality_metrics)
        for component in components:
            component_metrics = [m for m in quality_metrics if m.component == component]
            if component_metrics:
                avg_score = sum(m.value for m in component_metrics) / len(component_metrics)
                quality_by_component[component] = {
                    "avg_score": avg_score,
                    "samples": len(component_metrics),
                }

        return {
            "average_quality": sum(m.value for m in quality_metrics) / len(quality_metrics) if quality_metrics else 0,
            "quality_by_component": quality_by_component,
            "total_components_measured": len(components),
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of error metrics

        Returns:
            Dictionary with error statistics
        """
        # Calculate error rate by component
        error_metrics = [m for m in self.metrics if m.metric_type == MetricType.ERROR_RATE]
        error_by_component = {}

        components = set(m.component for m in error_metrics)
        for component in components:
            component_metrics = [m for m in error_metrics if m.component == component]
            if component_metrics:
                error_count = sum(1 for m in component_metrics if m.value > 0)
                error_rate = error_count / len(component_metrics)
                error_by_component[component] = {
                    "error_rate": error_rate,
                    "samples": len(component_metrics),
                    "error_count": error_count,
                }

        return {
            "total_errors": sum(1 for m in error_metrics if m.value > 0),
            "total_samples": len(error_metrics),
            "overall_error_rate": sum(1 for m in error_metrics if m.value > 0) / len(error_metrics) if error_metrics else 0,
            "error_by_component": error_by_component,
        }

    def _create_alert(self, message: str, severity: AlertSeverity, source: str, details: Dict[str, Any] = None) -> None:
        """
        Create a new alert

        Args:
            message: Alert message
            severity: Alert severity
            source: Alert source
            details: Additional details
        """
        timestamp = time.time()
        alert = Alert(
            message=message,
            severity=severity,
            source=source,
            timestamp=timestamp,
            details=details or {},
            resolved=False,
        )

        self.alerts.append(alert)

        # Log the alert
        log_level = logging.INFO
        if severity == AlertSeverity.WARNING:
            log_level = logging.WARNING
        elif severity == AlertSeverity.ERROR:
            log_level = logging.ERROR
        elif severity == AlertSeverity.CRITICAL:
            log_level = logging.CRITICAL

        logger.log(log_level, f"ALERT: {message} (Severity: {severity.value}, Source: {source})")

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback {callback.__name__}: {e}")

    def _save_metrics(self) -> None:
        """Save metrics to disk"""
        try:
            # Create a JSON-serializable list of metrics
            serializable_metrics = [
                {
                    "metric_type": m.metric_type.value,
                    "value": m.value,
                    "component": m.component,
                    "timestamp": m.timestamp,
                    "details": m.details,
                }
                for m in self.metrics
            ]

            # Save to file
            metrics_file = os.path.join(self.metrics_path, f"metrics_{int(time.time())}.json")
            with open(metrics_file, "w") as f:
                json.dump(serializable_metrics, f, indent=2)

            logger.debug(f"Saved {len(self.metrics)} metrics to {metrics_file}")
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def save_alerts(self) -> None:
        """Save alerts to disk"""
        try:
            # Create a JSON-serializable list of alerts
            serializable_alerts = [
                {
                    "message": a.message,
                    "severity": a.severity.value,
                    "source": a.source,
                    "timestamp": a.timestamp,
                    "details": a.details,
                    "resolved": a.resolved,
                }
                for a in self.alerts
            ]

            # Save to file
            alerts_file = os.path.join(self.metrics_path, f"alerts_{int(time.time())}.json")
            with open(alerts_file, "w") as f:
                json.dump(serializable_alerts, f, indent=2)

            logger.debug(f"Saved {len(self.alerts)} alerts to {alerts_file}")
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
