package com.euraka.client;

import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

import java.util.List;

@RestController
@RequestMapping("/product")
public class ProductController {
    private final DiscoveryClient discoveryClient;
    private final RestClient restClient;
    public ProductController(DiscoveryClient discoveryClient, RestClient restClient) {
        this.discoveryClient = discoveryClient;
        this.restClient = restClient;
    }

    @GetMapping("/fetch-order")
    public String fetchOrder() {
        List<ServiceInstance> instances = discoveryClient.getInstances("order-service");
        if (instances == null || instances.isEmpty()) {
            throw new RuntimeException("No order service instances found");
        }

        ServiceInstance instance = instances.getFirst();
        String url = instance.getUri().toString() + "/order/hello";
        System.out.println("Calling order-service at: " + url);
        return restClient.get()
                .uri(url)
                .retrieve()
                .body(String.class);

    }
}
