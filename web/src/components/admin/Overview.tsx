"use client";

import { Paper, Title } from "@mantine/core";

interface StatsCard {
  title: string;
  value: string;
  change: string;
  isIncrease: boolean;
  icon?: string;
}

interface TableData {
  id: string;
  name: string;
  email: string;
  status: "Active" | "Inactive" | "Pending";
  date: string;
}

interface Activity {
  text: string;
  time: string;
  type: "user" | "system" | "security" | "update";
}

export default function Overview() {
  const stats: StatsCard[] = [
    {
      title: "Total Users",
      value: "1,234",
      change: "+12.5%",
      isIncrease: true,
      icon: "👥",
    },
    {
      title: "Active Sessions",
      value: "423",
      change: "+5.25%",
      isIncrease: true,
      icon: "🔵",
    },
    {
      title: "Total Revenue",
      value: "$12,345",
      change: "-2.5%",
      isIncrease: false,
      icon: "💰",
    },
    {
      title: "Conversion Rate",
      value: "2.5%",
      change: "+0.5%",
      isIncrease: true,
      icon: "📈",
    },
  ];

  const recentActivity: Activity[] = [
    { text: "New user registration", time: "5 minutes ago", type: "user" },
    { text: "System update completed", time: "2 hours ago", type: "system" },
    { text: "Security alert detected", time: "3 hours ago", type: "security" },
    { text: "Database backup completed", time: "4 hours ago", type: "system" },
    { text: "New feature deployed", time: "5 hours ago", type: "update" },
  ];

  const tableData: TableData[] = [
    {
      id: "1",
      name: "John Doe",
      email: "john@example.com",
      status: "Active",
      date: "2024-03-20",
    },
    {
      id: "2",
      name: "Jane Smith",
      email: "jane@example.com",
      status: "Inactive",
      date: "2024-03-19",
    },
    {
      id: "3",
      name: "Bob Johnson",
      email: "bob@example.com",
      status: "Active",
      date: "2024-03-18",
    },
    {
      id: "4",
      name: "Alice Brown",
      email: "alice@example.com",
      status: "Pending",
      date: "2024-03-17",
    },
  ];

  const getActivityIcon = (type: Activity["type"]) => {
    switch (type) {
      case "user":
        return "👤";
      case "system":
        return "🔧";
      case "security":
        return "🔒";
      case "update":
        return "🚀";
      default:
        return "📝";
    }
  };

  const getStatusColor = (status: TableData["status"]) => {
    switch (status) {
      case "Active":
        return "bg-primary/20 text-primary";
      case "Inactive":
        return "bg-secondary/20 text-secondary";
      case "Pending":
        return "bg-accent/20 text-accent";
      default:
        return "bg-secondary/20 text-secondary";
    }
  };

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Paper
            key={index}
            className="p-6 bg-white/50 border border-primary/10 hover:shadow-md transition-all duration-200">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-2">{stat.icon}</span>
              <h3 className="text-sm text-primary/70">{stat.title}</h3>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-2xl font-semibold text-primary">
                {stat.value}
              </p>
              <span
                className={`text-sm px-2 py-1 rounded-full ${
                  stat.isIncrease
                    ? "bg-primary/20 text-primary"
                    : "bg-red-100 text-red-700"
                }`}>
                {stat.change}
              </span>
            </div>
          </Paper>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Paper className="lg:col-span-1 p-6 bg-white/50 border border-primary/10">
          <Title order={3} className="mb-6 text-gradient-theme">
            Recent Activity
          </Title>
          <div className="space-y-6">
            {recentActivity.map((activity, index) => (
              <div
                key={index}
                className="flex items-start space-x-3 pb-4 border-b border-primary/10 last:border-0 last:pb-0">
                <span className="text-xl mt-1">
                  {getActivityIcon(activity.type)}
                </span>
                <div className="flex-1">
                  <p className="text-sm text-primary/80">{activity.text}</p>
                  <span className="text-xs text-primary/60 mt-1">
                    {activity.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Paper>

        {/* Data Table */}
        <Paper className="lg:col-span-2 p-6 bg-white/50 border border-primary/10">
          <div className="flex justify-between items-center mb-6">
            <Title order={3} className="text-gradient-theme">
              Recent Users
            </Title>
            <button className="text-primary hover:text-primary/80 text-sm font-medium transition-colors">
              View All
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-primary/10">
                  <th className="text-left py-3 px-4 text-sm font-medium text-primary/70">
                    Name
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-primary/70">
                    Email
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-primary/70">
                    Status
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-primary/70">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((user) => (
                  <tr
                    key={user.id}
                    className="border-b border-primary/10 hover:bg-primary/5 transition-colors">
                    <td className="py-3 px-4 text-sm text-primary/90">
                      {user.name}
                    </td>
                    <td className="py-3 px-4 text-sm text-primary/80">
                      {user.email}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                          user.status
                        )}`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-primary/80">
                      {user.date}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Paper>
      </div>
    </div>
  );
}
