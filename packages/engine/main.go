package main

import (
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// 预算服务 - Go 实现高性能预算计算

type BudgetRequest struct {
	ProjectID   string         `json:"project_id"`
	Materials   []MaterialItem `json:"materials"`
	City        string         `json:"city"`
	BudgetLimit int            `json:"budget_limit,omitempty"`
}

type MaterialItem struct {
	Category string  `json:"category"`
	Space   string  `json:"space"`
	Item    string  `json:"item"`
	Spec    string  `json:"spec"`
	Unit    string  `json:"unit"`
	Quantity float64 `json:"quantity"`
	Price   int     `json:"price"` // 分
}

type BudgetSummary struct {
	MaterialCost   int `json:"material_cost"`
	LaborCost     int `json:"labor_cost"`
	ManagementFee int `json:"management_fee"`
	MiscCost      int `json:"misc_cost"`
	TotalCost     int `json:"total_cost"`
}

type BudgetResponse struct {
	ProjectID      string         `json:"project_id"`
	City           string         `json:"city"`
	CityCoef       float64       `json:"city_coefficient"`
	Items          []MaterialItem `json:"items"`
	Summary        BudgetSummary  `json:"summary"`
	Version        int            `json:"version"`
	UpdatedAt      string         `json:"updated_at"`
	BudgetWarning  *BudgetWarning `json:"budget_warning,omitempty"`
}

type BudgetWarning struct {
	IsOverBudget bool     `json:"is_over_budget"`
	OverAmount   int      `json:"over_amount"`
	Remaining    int      `json:"remaining"`
	WarningLevel string   `json:"warning_level"`
	Suggestions  []string `json:"suggestions"`
}

// 地区调价系数
var cityCoef = map[string]float64{
	"北京": 1.3,
	"上海": 1.25,
	"广州": 1.1,
	"深圳": 1.2,
	"成都": 0.95,
	"杭州": 1.15,
	"武汉": 0.9,
	"西安": 0.85,
	"默认": 1.0,
}

// 费率系数
const (
	LaborRate        = 0.4  // 人工费系数
	ManagementRate   = 0.1  // 管理费系数
	MiscRate         = 0.05 // 杂费系数
)

func main() {
	r := gin.Default()
	
	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})
	
	// 计算预算
	r.POST("/api/v1/budget/calculate", calculateBudget)
	
	// 预算红线检查
	r.POST("/api/v1/budget/check-warning", checkBudgetWarning)
	
	// 变更影响计算
	r.POST("/api/v1/budget/change-impact", calculateChangeImpact)
	
	log.Println("预算引擎启动，端口: 8080")
	r.Run(":8080")
}

func calculateBudget(c *gin.Context) {
	var req BudgetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 获取地区系数
	coef := cityCoef[req.City]
	if coef == 0 {
		coef = cityCoef["默认"]
	}
	
	var materialCost, laborCost int
	
	// 计算各项费用
	for i := range req.Materials {
		item := &req.Materials[i]
		// 应用地区系数
		totalPrice := int(float64(item.Price) * item.Quantity * coef)
		item.Price = totalPrice
		
		materialCost += totalPrice
		// 计算人工费
		laborCost += int(float64(totalPrice) * LaborRate)
	}
	
	// 计算管理费和杂费
	baseCost := materialCost + laborCost
	managementFee := int(float64(baseCost) * ManagementRate)
	miscCost := int(float64(baseCost) * MiscRate)
	totalCost := baseCost + managementFee + miscCost
	
	response := BudgetResponse{
		ProjectID: req.ProjectID,
		City:      req.City,
		CityCoef:  coef,
		Items:     req.Materials,
		Summary: BudgetSummary{
			MaterialCost:   materialCost,
			LaborCost:      laborCost,
			ManagementFee:  managementFee,
			MiscCost:       miscCost,
			TotalCost:      totalCost,
		},
		Version:   1,
		UpdatedAt: time.Now().Format(time.RFC3339),
	}
	
	// 检查预算红线
	if req.BudgetLimit > 0 {
		warning := checkBudgetLimit(totalCost, req.BudgetLimit)
		response.BudgetWarning = &warning
	}
	
	c.JSON(http.StatusOK, response)
}

func checkBudgetWarning(c *gin.Context) {
	var req struct {
		CurrentBudget int `json:"current_budget"`
		BudgetLimit   int `json:"budget_limit"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	warning := checkBudgetLimit(req.CurrentBudget, req.BudgetLimit)
	c.JSON(http.StatusOK, warning)
}

func checkBudgetLimit(currentBudget, budgetLimit int) BudgetWarning {
	remaining := budgetLimit - currentBudget
	warning := BudgetWarning{
		IsOverBudget: currentBudget > budgetLimit,
		Remaining:    remaining,
	}
	
	if currentBudget > budgetLimit {
		warning.OverAmount = currentBudget - budgetLimit
		if warning.OverAmount > budgetLimit/10 {
			warning.WarningLevel = "high"
		} else {
			warning.WarningLevel = "medium"
		}
		warning.Suggestions = []string{
			"考虑更换为性价比更高的材料",
			"适当减少装修项目",
			"调整装修档次",
		}
	} else if remaining < budgetLimit/10 {
		warning.WarningLevel = "low"
		warning.Suggestions = []string{"预算接近红线，注意控制"}
	} else {
		warning.WarningLevel = "normal"
	}
	
	return warning
}

func calculateChangeImpact(c *gin.Context) {
	var req struct {
		ProjectID     string `json:"project_id"`
		ChangeType    string `json:"change_type"`
		ChangeParam   map[string]interface{} `json:"change_param"`
		CurrentBudget int    `json:"current_budget"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	var impact = gin.H{
		"change_type":   req.ChangeType,
		"changed_items":  []interface{}{},
		"total_impact":   0,
		"impact_percentage": 0,
	}
	
	switch req.ChangeType {
	case "material_change":
		if oldPrice, ok := req.ChangeParam["old_price"].(float64); ok {
			if newPrice, ok := req.ChangeParam["new_price"].(float64); ok {
				if quantity, ok := req.ChangeParam["quantity"].(float64); ok {
					priceDiff := newPrice - oldPrice
					totalImpact := int(priceDiff * quantity)
					impact.(gin.H)["changed_items"] = []gin.H{
						{
							"item":       req.ChangeParam["item"],
							"old_price":  oldPrice,
							"new_price":  newPrice,
							"quantity":   quantity,
							"impact":     totalImpact,
						},
					}
					impact.(gin.H)["total_impact"] = totalImpact
				}
			}
		}
	case "area_change":
		if oldArea, ok := req.ChangeParam["old_area"].(float64); ok {
			if newArea, ok := req.ChangeParam["new_area"].(float64); ok {
				areaDiff := newArea - oldArea
				pricePerSqm := 1000.0
				if p, ok := req.ChangeParam["price_per_sqm"].(float64); ok {
					pricePerSqm = p
				}
				totalImpact := int(areaDiff * pricePerSqm)
				impact.(gin.H)["changed_items"] = []gin.H{
					{
						"type": "面积调整",
						"old_area": oldArea,
						"new_area": newArea,
						"impact":  totalImpact,
					},
				}
				impact.(gin.H)["total_impact"] = totalImpact
			}
		}
	case "layout_change":
		totalImpact := int(float64(req.CurrentBudget) * 0.15)
		impact.(gin.H)["changed_items"] = []gin.H{
			{
				"type":        "布局调整",
				"description": "涉及水电、墙体等多项变更",
				"impact":      totalImpact,
			},
		}
		impact.(gin.H)["total_impact"] = totalImpact
	}
	
	if req.CurrentBudget > 0 {
		impact.(gin.H)["impact_percentage"] = float64(impact.(gin.H)["total_impact"].(int)) / float64(req.CurrentBudget) * 100
	}
	
	c.JSON(http.StatusOK, impact)
}
